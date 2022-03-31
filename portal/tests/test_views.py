from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest import mock

from portal.models import Collection


class CollectionsViewTest(TestCase):
    """Test /collection/ view"""

    @classmethod
    def setUpTestData(cls):
        """Add some objects used by testing methods"""

        for col_id in range(5):
            file_name = 'file_%s.csv' % col_id
            col = Collection(file_name=file_name)
            col.file = SimpleUploadedFile(
                file_name,
                b'''name,height,mass,hair_color,skin_color,eye_color,birth_year,gender,homeworld,date
                Luke Skywalker,172,77,blond,fair,blue,19BBY,male,Tatooine,2014-12-20
                C-3PO,167,75,n/a,gold,yellow,112BBY,n/a,Tatooine,2014-12-20'''
            )
            col.save()

    def tearDown(self):
        """Delete al files created during the test"""

        for col in Collection.objects.all():
            col.file.delete()
            col.save()

    def test_view_url_exists_at_desired_location(self):
        """Test, if URL exists"""

        response = self.client.get('/collections/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Test, if URL is accessible by the name"""

        response = self.client.get(reverse('collections'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test, if the view is using the correct template"""

        response = self.client.get('/collections/')
        self.assertTemplateUsed(response, 'portal/collections.html')

    def test_context_collections(self):
        """Test, if view is passing correct context

        - There must be `collections` list in the context
        - `collections` length is correct
        """

        col_count = Collection.objects.all().count()
        response = self.client.get('/collections/')
        self.assertTrue('collections' in response.context)
        self.assertTrue(len(response.context['collections']) == col_count)

    @mock.patch('portal.swapi.SWAPI.planets_get')
    def test_post_swapi_error_planets(self, mock_planets):
        """Test correct behaviour after SWAPI/planets error

        - No collection is added - `collections` count must be correct.
        - Warning message is shown
        """

        mock_planets.return_value = None
        col_count = Collection.objects.all().count()
        response = self.client.post('/collections/')
        self.assertTrue(len(response.context['messages']) == 1)
        self.assertTrue(len(response.context['collections']) == col_count)

    @mock.patch('portal.swapi.SWAPI.planets_get')
    @mock.patch('portal.swapi.SWAPI.people_get')
    def test_post_swapi_error_people(self, mock_people, mock_planets):
        """Test correct behaviour after SWAPI/people error

        - No collection is added - `collections` count is correct.
        - Warning message is shown
        """

        mock_planets.return_value = [{'url': 'url', 'name': 'planet'}]
        mock_people.return_value = None
        col_count = Collection.objects.all().count()
        response = self.client.post('/collections/')
        self.assertTrue(len(response.context['messages']) == 1)
        self.assertTrue(len(response.context['collections']) == col_count)

    @mock.patch('portal.swapi.SWAPI.planets_get')
    @mock.patch('portal.swapi.SWAPI.people_get')
    def test_post_ok(self, mock_people, mock_planets):
        """Test correct behaviour after POST request went well

        - people and planets responses are processed
        - No message is shown
        - Show added collection within page - `collections` count i
            s increased
        """
        mock_planets.return_value = [{'url': 'url', 'name': 'planet'}]
        mock_people.return_value = [
            {'name': 'Luke Skywalker', 'height': '172', 'mass': '77',
             'hair_color': 'blond', 'skin_color': 'fair', 'eye_color': 'blue',
             'birth_year': '19BBY', 'gender': 'male',
             'homeworld': 'https://swapi.dev/api/planets/1/',
             'films': [
                 'https://swapi.dev/api/films/1/',
                 'https://swapi.dev/api/films/2/',
                 'https://swapi.dev/api/films/3/',
                 'https://swapi.dev/api/films/6/'],
             'species': [],
             'vehicles': [
                 'https://swapi.dev/api/vehicles/14/',
                 'https://swapi.dev/api/vehicles/30/'],
             'starships': [
                 'https://swapi.dev/api/starships/12/',
                 'https://swapi.dev/api/starships/22/'],
             'created': '2014-12-09T13:50:51.644000Z',
             'edited': '2014-12-20T21:17:56.891000Z',
             'url': 'https://swapi.dev/api/people/1/'},
            {'name': 'C-3PO', 'height': '167', 'mass': '75',
             'hair_color': 'n/a', 'skin_color': 'gold', 'eye_color': 'yellow',
             'birth_year': '112BBY', 'gender': 'n/a',
             'homeworld': 'https://swapi.dev/api/planets/1/',
             'films': [
                 'https://swapi.dev/api/films/1/',
                 'https://swapi.dev/api/films/2/',
                 'https://swapi.dev/api/films/3/',
                 'https://swapi.dev/api/films/4/',
                 'https://swapi.dev/api/films/5/',
                 'https://swapi.dev/api/films/6/'],
             'species': ['https://swapi.dev/api/species/2/'], 'vehicles': [],
             'starships': [], 'created': '2014-12-10T15:10:51.357000Z',
             'edited': '2014-12-20T21:17:50.309000Z',
             'url': 'https://swapi.dev/api/people/2/'}
        ]
        col_count = Collection.objects.all().count()
        response = self.client.post('/collections/')
        self.assertTrue(len(response.context['messages']) == 0)
        self.assertTrue(len(response.context['collections']) == col_count + 1)


class CollectionDetailViewTest(TestCase):
    """Test /collection_detail/ view

    :cvar TEST_FILE_NAME: Create testing object with the name.
        During tests, obtained object's name must be the same
    :cvar TEST_INSTANCE_PK: Primary key of `Collection` object
        instance used later within tests
    """

    TEST_FILE_NAME = 'file.csv'
    TEST_INSTANCE_PK = None

    @classmethod
    def setUpTestData(cls):
        """Set the object used by testing methods"""

        col = Collection(file_name=cls.TEST_FILE_NAME)
        col.file = SimpleUploadedFile(
            cls.TEST_FILE_NAME,
            b'''name,height,mass,hair_color,skin_color,eye_color,birth_year,gender,homeworld,date
            Luke Skywalker,172,77,blond,fair,blue,19BBY,male,Tatooine,2014-12-20
            C-3PO,167,75,n/a,gold,yellow,112BBY,n/a,Tatooine,2014-12-20
            R2-D2,96,32,n/a,"white, blue",red,33BBY,n/a,Naboo,2014-12-20
            Darth Vader,202,136,none,white,yellow,41.9BBY,male,Tatooine,2014-12-20
            Leia Organa,150,49,brown,light,brown,19BBY,female,Alderaan,2014-12-20
            Owen Lars,178,120,"brown, grey",light,blue,52BBY,male,Tatooine,2014-12-20
            Beru Whitesun lars,165,75,brown,light,blue,47BBY,female,Tatooine,2014-12-20
            R5-D4,97,32,n/a,"white, red",red,unknown,n/a,Tatooine,2014-12-20
            Biggs Darklighter,183,84,black,light,brown,24BBY,male,Tatooine,2014-12-20
            Obi-Wan Kenobi,182,77,"auburn, white",fair,blue-gray,57BBY,male,Stewjon,2014-12-20
            Anakin Skywalker,188,84,blond,fair,blue,41.9BBY,male,Tatooine,2014-12-20'''
        )
        col.save()
        cls.TEST_INSTANCE_PK = col.pk

    @classmethod
    def tearDownClass(cls):
        """Delete the files after all tests are finished"""

        for col in Collection.objects.all():
            col.file.delete()
            col.save()

    def test_view_url_exists_at_desired_location(self):
        """Test, if URL exists"""

        response = self.client.get(
            '/collections/{}/'.format(self.TEST_INSTANCE_PK))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Test, if URL is accessible by the name"""

        response = self.client.get(
            reverse('collection_detail',
                    kwargs={'collection_id': self.TEST_INSTANCE_PK}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test, if the view is using the correct template"""

        response = self.client.get(
            '/collections/{}/'.format(self.TEST_INSTANCE_PK))
        self.assertTemplateUsed(response, 'portal/collection_detail.html')

    def test_view_collection_unknown(self):
        """Test correct behaviour for unknown collection

        Response is redirected to `/collections/` view
        """

        response = self.client.get('/collections/123456/')
        self.assertRedirects(response, '/collections/')

    def test_view_collection_id_incorrect(self):
        """Test correct behaviour for incorrect collection_id (str)

        Response is redirected to `/collections/` view
        """

        response = self.client.get('/collections/qwert/')
        self.assertRedirects(response, '/collections/')

    def test_view_collection_first_page(self):
        """Test correct behaviour for the collection - first page

        Check, if response is rendered with correct context:
        - `col_name` is present
        - `col_id` is 1
        - `next_page` is 2
        - `col_header` length is 10
        - `col_data` is 10
        """

        response = self.client.get(
            '/collections/{}/'.format(self.TEST_INSTANCE_PK))
        self.assertTrue(response.context['col_name'] == self.TEST_FILE_NAME)
        self.assertTrue(response.context['col_id'] == self.TEST_INSTANCE_PK)
        self.assertTrue(len(response.context['col_header']) == 10)
        self.assertTrue(len(response.context['col_data']) == 10)
        self.assertTrue(response.context['next_page'] == 2)

    def test_view_collection_second_page(self):
        """Test correct behaviour for the collection - second page

        Check, if response is rendered with correct context.
        This is the last, page, so only 1 row is displayed and
        next page is the first:
        - `col_name` is present
        - `col_id` is 1
        - `next_page` is 1
        - `col_header` length is 10
        - `col_data` is 1
        """

        response = self.client.get(
            '/collections/{}/?page=2'.format(self.TEST_INSTANCE_PK))
        self.assertTrue(response.context['col_name'] == self.TEST_FILE_NAME)
        self.assertTrue(response.context['col_id'] == self.TEST_INSTANCE_PK)
        self.assertTrue(len(response.context['col_header']) == 10)
        self.assertTrue(len(response.context['col_data']) == 1)
        self.assertTrue(response.context['next_page'] == 1)


class CollectionStatViewTest(TestCase):
    """Test /collection_stats/ view

    :cvar TEST_FILE_NAME: Create testing object with the name.
        During tests, obtained object's name must be the same
    :cvar TEST_INSTANCE_PK: Primary key of `Collection` object
        instance used later within tests
    """

    TEST_FILE_NAME = 'file.csv'
    TEST_INSTANCE_PK = None

    @classmethod
    def setUpTestData(cls):
        """Set the object used by testing methods"""

        col = Collection(file_name=cls.TEST_FILE_NAME)
        col.file = SimpleUploadedFile(
            cls.TEST_FILE_NAME,
            b'''name,height,mass,hair_color,skin_color,eye_color,birth_year,gender,homeworld,date
            Luke Skywalker,172,77,blond,fair,blue,19BBY,male,Tatooine,2014-12-20
            C-3PO,167,75,n/a,gold,yellow,112BBY,n/a,Tatooine,2014-12-20
            R2-D2,96,32,n/a,"white, blue",red,33BBY,n/a,Naboo,2014-12-20
            Darth Vader,202,136,none,white,yellow,41.9BBY,male,Tatooine,2014-12-20
            Leia Organa,150,49,brown,light,brown,19BBY,female,Alderaan,2014-12-20
            Owen Lars,178,120,"brown, grey",light,blue,52BBY,male,Tatooine,2014-12-20
            Beru Whitesun lars,165,75,brown,light,blue,47BBY,female,Tatooine,2014-12-20
            R5-D4,97,32,n/a,"white, red",red,unknown,n/a,Tatooine,2014-12-20
            Biggs Darklighter,183,84,black,light,brown,24BBY,male,Tatooine,2014-12-20
            Obi-Wan Kenobi,182,77,"auburn, white",fair,blue-gray,57BBY,male,Stewjon,2014-12-20
            Anakin Skywalker,188,84,blond,fair,blue,41.9BBY,male,Tatooine,2014-12-20'''
        )
        col.save()
        cls.TEST_INSTANCE_PK = col.pk

    @classmethod
    def tearDownClass(cls):
        """Delete the files after all tests are finished"""

        for col in Collection.objects.all():
            col.file.delete()
            col.save()

    def test_view_url_exists_at_desired_location(self):
        """Test, if URL exists"""

        response = self.client.get(
            '/collections/{}/stats/'.format(self.TEST_INSTANCE_PK))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Test, if URL is accessible by the name"""

        response = self.client.get(
            reverse('collection_stats',
                    kwargs={'collection_id': self.TEST_INSTANCE_PK}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test, if the view is using the correct template"""

        response = self.client.get(
            '/collections/{}/stats/'.format(self.TEST_INSTANCE_PK))
        self.assertTemplateUsed(response, 'portal/collection_stats.html')

    def test_view_collection_unknown(self):
        """Test correct behaviour for unknown collection

        Response is redirected to `/collections/` view
        """

        response = self.client.get('/collections/123456/stats/')
        self.assertRedirects(response, '/collections/')

    def test_view_collection_id_incorrect(self):
        """Test correct behaviour for incorrect collection_id (str)

        Response is redirected to `/collections/` view
        """

        response = self.client.get('/collections/qwert/stats/')
        self.assertRedirects(response, '/collections/')

    def test_view_no_field_selected(self):
        """Test the view when no fields are selected

        There must not be `col_header` nor `col_data` in context
        """

        response = self.client.get(
            '/collections/{}/stats/'.format(self.TEST_INSTANCE_PK))
        self.assertTrue(response.context.get('col_header') is None)
        self.assertTrue(response.context.get('col_data') is None)

    def test_view_fields_selected(self):
        """Test the view when two fields are selected

        - There must be `col_header` containing tuple
            ('eye_color', 'name', 'count')
        - There must be `col_data` in the context with length of 11:
            all the data from the table
        """

        response = self.client.get(
            '/collections/{}/stats/?eye_color=on&name=on'.format(
                self.TEST_INSTANCE_PK))
        self.assertTrue(response.context['col_header'] == (
            'eye_color', 'name', 'count'))
        self.assertTrue(len(response.context['col_data']) == 11)

    def test_view_na_fields_selected(self):
        """Test the view when two fields are selected.
        Some values are `n/a`

        - There must be `col_header` in the context with length of 3
            ('eye_color', 'gender', 'count')
        - There must be `col_data` in the context with length of 11:
            all the data from the table
        """

        response = self.client.get(
            '/collections/{}/stats/?eye_color=on&gender=on'.format(
                self.TEST_INSTANCE_PK))
        self.assertTrue(response.context['col_header'] == (
            'eye_color', 'gender', 'count'))
        self.assertTrue(len(response.context['col_data']) == 8)
