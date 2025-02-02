import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker
from apps.core.models import (
    User,
    Category,
    Course,
    Cart,
    Video,
    Question,
    Choice,
    Purchase,
    Certificate,
    Rate,
    Grade,
)


class Command(BaseCommand):
    help = "Populate the database with dummy data"

    def handle(self, *args, **kwargs):
        # Create users
        fake = Faker()
        students = [
            User.objects.create_user(
                # username=f"student{i}",
                first_name=fake.first_name(),
                middle_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                password=fake.password(),
            )
            for i in range(100)
        ]
        instructors = [
            User.objects.create_user(
                # username=f"student{i}",
                first_name=fake.first_name(),
                middle_name=fake.last_name(),
                last_name=fake.name(),
                email=fake.email(),
                password=fake.password(),
                is_instructor=True,
            )
            for i in range(5)
        ]
        # self.stdout.write(
        #     f"Created {len(students)} students and {len(instructors)} instructors."
        # )

        # Create categories
        categories = [Category.objects.create(name=fake.word()) for _ in range(3)]
        self.stdout.write(f"Created {len(categories)} categories.")

        # Create courses
        courses = []
        for i in range(5):
            course = Course.objects.create(
                instructor=random.choice(instructors),
                name=f"Course {i+1}",
                slug=f"course-{i+1}",
                description=fake.text(),
                price=random.uniform(50, 500),
                discount=random.randint(5, 50),
                category=random.choice(categories),
                duration=timedelta(hours=random.randint(5, 20)),
            )
            courses.append(course)
        self.stdout.write(f"Created {len(courses)} courses.")

        # Add videos to courses
        videos = []
        for course in courses:
            for i in range(3):
                video = Video.objects.create(
                    course=course,
                    video=f"video_{course.slug}_{i}.mp4",
                    name=f"Video {i+1} for {course.name}",
                    counter=i + 1,
                )
                videos.append(video)
        self.stdout.write(f"Created {len(videos)} videos.")

        # Add questions and choices for videos
        questions = []
        for video in videos:
            for i in range(2):
                question = Question.objects.create(
                    video=video,
                    question=fake.sentence(),
                )
                for j in range(4):  # 4 choices per question
                    choice = Choice.objects.create(
                        question=question,
                        choice=f"Choice {j+1} for question {i+1}",
                    )
                question.right_answer = random.choice(question.choice_set.all())
                question.save()
                questions.append(question)
        self.stdout.write(f"Created {len(questions)} questions with choices.")

        # Enroll students in courses (simulate purchases)
        purchases = []
        for student in students:
            enrolled_courses = random.sample(courses, random.randint(1, 3))
            for course in enrolled_courses:
                purchase = Purchase.objects.create(
                    student=student,
                    course=course,
                )
                purchases.append(purchase)
        self.stdout.write(f"Created {len(purchases)} purchases.")

        # Rate courses
        rates = []
        for student in students:
            rated_courses = random.sample(courses, random.randint(1, 3))
            for course in rated_courses:
                rate = Rate.objects.create(
                    student=student,
                    course=course,
                    rate=str(random.randint(1, 5)),
                    review_text=fake.text(),
                )
                rates.append(rate)
        self.stdout.write(f"Created {len(rates)} ratings.")

        # Add grades for videos
        grades = []
        for student in students:
            for video in random.sample(videos, random.randint(5, 10)):
                grade = Grade.objects.create(
                    student=student,
                    video=video,
                    passed=random.choice([True, False]),
                )
                grades.append(grade)
        self.stdout.write(f"Created {len(grades)} grades.")

        self.stdout.write(self.style.SUCCESS("Dummy data added successfully!"))
