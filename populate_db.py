from jobs.models import User, ShopProfile, JobVacancy

def create_mock_data():
    print("Starting database population...")

    # Define standard mock password
    password = 'ComplexPass123!'

    # --- 1. Create Users (Shop Owners) ---
    owners = [
        {'username': 'owner_cafe', 'email': 'cafe@local.store', 'mobile_number': '5550001001', 'is_shop_owner': True},
        {'username': 'owner_tech', 'email': 'tech@local.store', 'mobile_number': '5550001002', 'is_shop_owner': True},
        {'username': 'owner_gym', 'email': 'gym@local.store', 'mobile_number': '5550001003', 'is_shop_owner': True}
    ]

    created_owners = []
    for o_data in owners:
        user, created = User.objects.get_or_create(
            username=o_data['username'],
            defaults={
                'email': o_data['email'],
                'mobile_number': o_data['mobile_number']
            }
        )
        # Assuming there is a role field in your custom user model as seen in jobs/models.py
        user.role = 'SHOP_OWNER'
        if created:
            user.set_password(password)
        user.save()
        if created:
            print(f"Created user: {user.username}")
        created_owners.append(user)

    # --- 2. Create Shop Profiles ---
    shops = [
        {
            'user': created_owners[0],
            'company_name': 'Sunrise Coffee Bean',
            'description': 'A bustling local coffee shop known for its artisanal roasts, friendly atmosphere, and incredible morning pastries. We prioritize community and fair-trade sourcing in everything we do.',
            'location': '123 Main Street, Downtown',
            'is_verified': True,
            'latitude': 40.7580,
            'longitude': -73.9855
        },
        {
            'user': created_owners[1],
            'company_name': 'Quantum Electronics Repair',
            'description': 'Your neighborhood tech experts! We repair everything from smartphones to vintage audio equipment. Fast turnaround times, transparent pricing, and a passion for keeping technology alive.',
            'location': '45 Tech Boulevard, Northside',
            'is_verified': True,
            'latitude': 40.7610,
            'longitude': -73.9800
        },
        {
            'user': created_owners[2],
            'company_name': 'Iron Core Athletics',
            'description': 'A premium local fitness center focused on strength training and high-intensity classes. We offer state-of-the-art equipment and dedicated personal trainers to help our members achieve their peak physical condition.',
            'location': '88 Fitness Way, West End',
            'is_verified': True,
            'latitude': 40.7550,
            'longitude': -73.9900
        }
    ]

    created_shops = []
    for s_data in shops:
        shop, created = ShopProfile.objects.get_or_create(
            user=s_data['user'],
            defaults={
                'company_name': s_data['company_name'],
                'description': s_data['description'],
                'location': s_data['location'],
                'is_verified': s_data['is_verified'],
                'latitude': s_data['latitude'],
                'longitude': s_data['longitude']
            }
        )
        if created:
            print(f"Created shop profile: {shop.company_name}")
        created_shops.append(shop)

    # --- 3. Create Job Vacancies ---
    jobs = [
        # Coffee Shop Jobs
        {
            'shop': created_shops[0],
            'title': 'Lead Barista',
            'job_type': 'FULL_TIME',
            'description': 'We are looking for an experienced Lead Barista to craft exceptional coffee beverages and help manage our morning rush schedule.',
            'skills_required': 'Latte Art, espresso calibration, customer service.',
            'experience_required': '2-3 Years',
            'education_required': 'High School Diploma',
            'salary_range': '$18 - $22 / hr',
            'is_active': True,
        },
        {
            'shop': created_shops[0],
            'title': 'Weekend Shift Cashier',
            'job_type': 'PART_TIME',
            'description': 'Friendly face needed to handle transactions and pastry displays during our busy Saturday and Sunday shifts.',
            'skills_required': 'Punctuality, friendly demeanor, handling cash.',
            'experience_required': 'Entry Level',
            'education_required': 'High School Student / Graduate',
            'salary_range': '$15 / hr',
            'is_active': True,
        },
        # Tech Repair Jobs
        {
            'shop': created_shops[1],
            'title': 'Junior Mobile Technician',
            'job_type': 'FULL_TIME',
            'description': 'Assist our senior repair techs with screen replacements, battery swaps, and diagnostic testing for iOS and Android devices.',
            'skills_required': 'Basic understanding of mobile architecture. Micro-soldering is a plus.',
            'experience_required': '1 Year',
            'education_required': 'Vocational Training / Certifications',
            'salary_range': '$40,000 - $50,000 / yr',
            'is_active': True,
        },
        {
            'shop': created_shops[1],
            'title': 'Customer Intake Specialist',
            'job_type': 'CONTRACT',
            'description': 'Greet customers, log hardware issues into our ticketing system, and provide initial estimates.',
            'skills_required': 'Excellent communication and basic typing skills.',
            'experience_required': 'None',
            'education_required': 'High School Diploma',
            'salary_range': '$17 / hr',
            'is_active': True,
        },
        # Gym Jobs
        {
            'shop': created_shops[2],
            'title': 'Certified Personal Trainer',
            'job_type': 'PART_TIME',
            'description': 'Run private 1-on-1 sessions and lead high-intensity group classes during the evening peak hours.',
            'skills_required': 'NASM, ACE, or ISSA certification. CPR/AED certified.',
            'experience_required': 'Certification Required',
            'education_required': 'Related Degree / Certs',
            'salary_range': '$35 / hr',
            'is_active': True,
        },
    ]

    for j_data in jobs:
        job, created = JobVacancy.objects.get_or_create(
            shop=j_data['shop'],
            title=j_data['title'],
            defaults={
                'job_type': j_data['job_type'],
                'description': j_data['description'],
                'skills_required': j_data['skills_required'],
                'experience_required': j_data['experience_required'],
                'education_required': j_data['education_required'],
                'salary_range': j_data['salary_range'],
                'is_active': j_data['is_active']
            }
        )
        if created:
            print(f"Created job vacancy: {job.title} at {job.shop.company_name}")

    print("Database population complete!")

create_mock_data()
