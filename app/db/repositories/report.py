
from sqlalchemy import select
from db.model.report import Report
from schemas.report import ReportCreate, ReportOut
from sqlalchemy.ext.asyncio import AsyncSession


class ReportRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def  create(self, report_data: ReportCreate):
        report = Report(**report_data.model_dump())
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return ReportOut.model_validate(report)
    
    async def get(self, report_id: int):
        report = await self.session.get(Report, report_id)
        if report:
            return ReportOut.model_validate(report)
        return None
    
    async def get_all(self):
        result = await self.session.execute(
            select(Report).order_by(Report.created_at.desc())
        )
        reports = result.scalars().all()
        return [ReportOut.model_validate(report) for report in reports]