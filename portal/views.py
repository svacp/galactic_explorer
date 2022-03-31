from django.shortcuts import render, redirect
from portal import swapi
from portal import models
import petl as etl
import dateutil.parser
import os
import uuid
from django.conf import settings
from django.contrib import messages

from portal import forms


def view_index(request):

    return redirect('collections')


def view_collections(request):
    """View for processing collections list.

    In case of POST request:
        - Get list of people from SW API
        - Transform the data
            - Parse date of edited column
            - Parse homeworld column to use the planet name
                instead of url
            - Cut some redundant columns
        - Load the data into CSV file
        - Save metadata into DB

    param request: HTTP Request object
    :returns: HTTP response: A page with list of previously fetched
        collections. In case of error during new collection fetching,
        show warning message.
    """

    def collections_render():
        """Helper method to get all previously fetched collections
        and render it
        """

        collections = models.Collection.objects.all()
        return render(
            request,
            'portal/collections.html',
            context={'collections': collections})

    if request.method == 'POST':
        s = swapi.SWAPI()

        # Get planets and fetch 'em to dict for latter use
        resp_planets = s.planets_get()
        if resp_planets is None:
            messages.warning(
                request, 'Error processing Star Wars API request :(')
            return collections_render()
        planets_map = {p['url']: p['name'] for p in resp_planets}

        # Get all people from the API
        resp_people = s.people_get()
        if resp_people is None:
            messages.warning(
                request, 'Error processing Star Wars API request :(')
            return collections_render()

        # Transform people data
        table = (
            etl
            .fromdicts(resp_people)
            .addfield(
                'date', lambda rec: dateutil.parser.parse(
                    rec['edited']).strftime('%Y-%m-%d'))
            .convert(
                'homeworld', lambda v: planets_map.get(v, 'N/A'))
            .cutout(
                'films', 'vehicles', 'starships', 'created',
                'url', 'species', 'edited')
        )

        # Load data into CSV file
        file_name = '%s.csv' % uuid.uuid4().hex
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        etl.tocsv(table, file_path)

        # Save metadata into model
        col = models.Collection(file_name=file_name)
        col.file.name = file_name
        col.save()

    return collections_render()


def view_collection_detail(request, collection_id):
    """View for processing collection detail.

    - Get collection CSV file
    - Load data from file respecting paging:
        - Requested page number is obtained from GET parameter `page`
        - There is support just for subsequent pages: Just `next`
            button is shown
        - When there is no data on next page, show the first page

    :param request: HTTP Request object
    :param collection_id: ID af the collection
    :return: HTTP response: A page with table data regarding given
        collection. In case of incorrect collection_id, redirect
        to collections list page.
    """

    # Get collection object
    try:
        col = models.Collection.objects.get(id=collection_id)
    except (models.Collection.DoesNotExist, ValueError):
        messages.warning(
            request, 'Given collection was lost in a black hole :(')
        return redirect('collections')

    # Get and read collection file
    file_path = os.path.join(settings.MEDIA_ROOT, col.file_name)
    table = etl.fromcsv(file_path)
    header = etl.header(table)

    # Get requested page number and data slice boundaries
    page = request.GET.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        page = 1
    slice_start = (page - 1) * 10
    slice_stop = slice_start + 10

    # Get data
    data = etl.records(table, slice_start, slice_stop)
    next_page = page + 1
    if len(data) < 10:
        next_page = 1

    return render(
        request,
        'portal/collection_detail.html',
        context={
            'col_name': col.file_name,
            'col_id': col.id,
            'col_header': header,
            'col_data': data,
            'next_page': next_page})


def view_collection_stats(request, collection_id):
    """View for processing collection Statistic.

    The statistic enables user to show count of occurrences of values
    for columns. Requested column names are retrieved from GET data
    (GET is used so user is able to bookmark the form).

    - Get collection CSV file
    - Transform data using `petl`: Find distinct values for the
        given fields and count the number of occurrences.

    :param request: HTTP Request object
    :param collection_id: ID af the collection
    :return: HTTP response: A page with table data regarding given
        collection statistics. In case of incorrect collection_id,
        redirect to collections list page.
    """

    # Get collection object
    try:
        col = models.Collection.objects.get(pk=collection_id)
    except (models.Collection.DoesNotExist, ValueError):
        messages.warning(
            request, 'Given collection was lost in a black hole :(')
        return redirect('collections')

    # Get collection object
    file_path = os.path.join(settings.MEDIA_ROOT, col.file_name)
    table = etl.fromcsv(file_path)

    # Process form: Get just form data keys as form contains
    # only checkboxes
    form = forms.StatisticsForm(request.GET)
    selected_fields = tuple(form.data.keys())

    # Use does not select any field. Do not show table
    if not selected_fields:
        return render(
            request,
            'portal/collection_stats.html',
            context={
                'col_name': col.file_name,
                'col_id': col.id,
                'form': form})

    # Count the values and return table data
    table_updated = (
        etl
        .valuecounts(table, *selected_fields)
        .cutout('frequency')
    )
    header = etl.header(table_updated)
    data = etl.records(table_updated)
    return render(
        request,
        'portal/collection_stats.html',
        context={
            'col_name': col.file_name,
            'col_id': col.id,
            'col_header': header,
            'col_data': data,
            'form': form})
