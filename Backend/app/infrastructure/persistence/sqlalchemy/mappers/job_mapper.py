from app.domain.entities.job import Job
from app.domain.value_objects.salary import Salary
from app.domain.value_objects.location import Location
from app.domain.value_objects.job_type import JobType
from app.domain.value_objects.experience_level import ExperienceLevel
from app.infrastructure.persistence.sqlalchemy.models.job_orm import JobORM


class JobMapper:
    """Mapper to convert between Job domain entity and JobORM model."""

    @staticmethod
    def to_domain(orm_job: JobORM) -> Job:
        """Convert SQLAlchemy JobORM to Job domain entity."""
        if not orm_job:
            return None
            
        return Job(
            id=orm_job.id,
            title=orm_job.title,
            company=orm_job.company,
            location=Location.from_string(orm_job.location) if orm_job.location else Location.remote(),
            salary=Salary.from_range(
                orm_job.salary_min,
                orm_job.salary_max,
                orm_job.salary_currency or "USD"
            ),
            job_type=JobType.from_string(orm_job.job_type) if orm_job.job_type else None,
            experience_level=ExperienceLevel.from_string(orm_job.experience_level) if orm_job.experience_level else None,
            description=orm_job.description,
            requirements=orm_job.requirements or [],
            benefits=orm_job.benefits or [],
            source=orm_job.source,
            source_url=orm_job.source_url,
            source_job_id=orm_job.source_job_id,
            posted_date=orm_job.posted_date,
            deadline=orm_job.deadline,
            company_logo_url=orm_job.company_logo_url,
            company_website=orm_job.company_website,
            skills=orm_job.skills or [],
            source_url_direct=orm_job.source_url_direct,
            company_industry=orm_job.company_industry,
            company_addresses=orm_job.company_addresses,
            company_num_employees=orm_job.company_num_employees,
            company_revenue=orm_job.company_revenue,
            company_description=orm_job.company_description,
            company_rating=orm_job.company_rating,
            company_reviews_count=orm_job.company_reviews_count,
            job_level=orm_job.job_level,
            job_function=orm_job.job_function,
            experience_range=orm_job.experience_range,
            emails=orm_job.emails or [],
            banner_photo_url=orm_job.banner_photo_url,
            vacancy_count=orm_job.vacancy_count,
            work_from_home_type=orm_job.work_from_home_type,
            view_count=orm_job.view_count,
            apply_count=orm_job.apply_count,
            created_at=orm_job.created_at,
            updated_at=orm_job.updated_at,
            scraped_at=orm_job.scraped_at
        )

    @staticmethod
    def to_orm(domain_job: Job) -> JobORM:
        """Convert Job domain entity to SQLAlchemy JobORM."""
        if not domain_job:
            return None
            
        return JobORM(
            id=domain_job.id,
            title=domain_job.title,
            company=domain_job.company,
            location=domain_job.location.format() if domain_job.location else None,
            salary_min=domain_job.salary.min_amount if domain_job.salary else None,
            salary_max=domain_job.salary.max_amount if domain_job.salary else None,
            salary_currency=domain_job.salary.currency if domain_job.salary else None,
            job_type=domain_job.job_type.value if domain_job.job_type else None,
            experience_level=domain_job.experience_level.value if domain_job.experience_level else None,
            description=domain_job.description,
            requirements=domain_job.requirements,
            benefits=domain_job.benefits,
            source=domain_job.source,
            source_url=domain_job.source_url,
            source_job_id=domain_job.source_job_id,
            posted_date=domain_job.posted_date,
            deadline=domain_job.deadline,
            company_logo_url=domain_job.company_logo_url,
            company_website=domain_job.company_website,
            skills=domain_job.skills,
            is_remote=domain_job.is_remote(),
            source_url_direct=domain_job.source_url_direct,
            company_industry=domain_job.company_industry,
            company_addresses=domain_job.company_addresses,
            company_num_employees=domain_job.company_num_employees,
            company_revenue=domain_job.company_revenue,
            company_description=domain_job.company_description,
            company_rating=domain_job.company_rating,
            company_reviews_count=domain_job.company_reviews_count,
            job_level=domain_job.job_level,
            job_function=domain_job.job_function,
            experience_range=domain_job.experience_range,
            emails=domain_job.emails,
            banner_photo_url=domain_job.banner_photo_url,
            vacancy_count=domain_job.vacancy_count,
            work_from_home_type=domain_job.work_from_home_type,
            view_count=domain_job.view_count,
            apply_count=domain_job.apply_count,
            created_at=domain_job.created_at,
            updated_at=domain_job.updated_at,
            scraped_at=domain_job.scraped_at
        )
