# File: tests/test_models.py
from django.test import TestCase
from src.models import Project

class ProjectModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Project.objects.create(project_idea="Project Apollo", executive_summary="A summary about Project Apollo.")

    def test_project_idea_label(self):
        project = Project.objects.get(id=1)
        field_label = project._meta.get_field('project_idea').verbose_name
        self.assertEqual(field_label, 'project idea')

    def test_executive_summary_label(self):
        project = Project.objects.get(id=1)
        field_label = project._meta.get_field('executive_summary').verbose_name
        self.assertEqual(field_label, 'executive summary')

    def test_project_idea_max_length(self):
        project = Project.objects.get(id=1)
        max_length = project._meta.get_field('project_idea').max_length
        self.assertEqual(max_length, 255)

    def test_object_name_is_project_idea(self):
        project = Project.objects.get(id=1)
        expected_object_name = project.project_idea
        self.assertEqual(str(project), expected_object_name)

    def test_project_creation(self):
        project = Project.objects.create(project_idea="New Project", executive_summary="Summary of the new project.")
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(project.project_idea, "New Project")
        self.assertEqual(project.executive_summary, "Summary of the new project.")

    def test_project_idea_cannot_be_blank(self):
        with self.assertRaises(Exception):  # Replace Exception with the specific exception Django raises for a blank CharField
            Project.objects.create(project_idea="", executive_summary="Summary without a project idea.")

    def test_executive_summary_cannot_be_blank(self):
        with self.assertRaises(Exception):  # Replace Exception with the specific exception Django raises for a blank TextField
            Project.objects.create(project_idea="Project with no summary", executive_summary="")

    def test_str_representation(self):
        project = Project.objects.get(id=1)
        self.assertEqual(str(project), "Project Apollo")

    @classmethod
    def tearDownClass(cls):
        # Cleanup any resources if needed
        pass