from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from portal.models import Collection


class CollectionModelTest(TestCase):
    """Test models module

    :cvar TEST_FILE_NAME: Create testing object with the name.
        During tests, obtained object's name must be the same
    :cvar TEST_FILE_CONTENT: Create testing object with the content.
        During tests, obtained object's content must be the same
    :cvar TEST_INSTANCE_PK: Primary key of `Collection` object
        instance used later within tests
    """

    TEST_FILE_NAME = 'TEST.csv'
    TEST_FILE_CONTENT = b'test file content'
    TEST_INSTANCE_PK = None

    @classmethod
    def setUpTestData(cls):
        """Set the object used by all testing methods"""

        col = Collection(file_name=cls.TEST_FILE_NAME)
        col.file = SimpleUploadedFile(
            cls.TEST_FILE_NAME,
            cls.TEST_FILE_CONTENT
        )
        col.save()
        cls.TEST_INSTANCE_PK = col.pk

    @classmethod
    def tearDownClass(cls):
        """Delete the file after all tests are finished"""

        col = Collection.objects.get(pk=cls.TEST_INSTANCE_PK)
        col.file.delete()
        col.save()

    def test_file_name(self):
        """Test file name match"""

        col = Collection.objects.get(pk=self.TEST_INSTANCE_PK)
        self.assertEqual(col.file_name, self.TEST_FILE_NAME)

    def test_file_read(self):
        """Test file content match"""

        col = Collection.objects.get(pk=self.TEST_INSTANCE_PK)
        file_content = col.file.read()
        self.assertEqual(file_content, self.TEST_FILE_CONTENT)
