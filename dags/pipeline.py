import logging
from datetime import timedelta

import pendulum
from airflow.sdk import dag, task

from src.database import save_paper
from src.html_generator import write_html
from src.llm import extract_metadata
from src.notifications import notify_discord
from src.convert import find_pdfs, pdf_to_markdown

LOGGER = logging.getLogger(__name__)

@dag(
    dag_id='research_paper_pipeline',
    description='Google Drive indexation',
    schedule='*/15 * * * *',
    start_date=pendulum.datetime(2026, 1, 1, tz='Europe/Brussels'),
    catchup=False,
    max_active_runs=1
)
def research_paper_pipeline():
    @task(retries=1, retry_delay=timedelta(minutes=2))
    def scan_papers() -> list[str]:
        names = find_pdfs()
        LOGGER.info('%d new pdf : %s', len(names), names)
        return names

    @task(retries=1, retry_delay=timedelta(minutes=2))
    def process_papers(filenames: list[str]) -> list[dict]:
        new_papers = []
        for filename in filenames:
            LOGGER.info('treating pdf : %s', filename)
            markdown = pdf_to_markdown(filename)
            metadata = extract_metadata(markdown, filename)
            if save_paper(filename, metadata):
                new_papers.append({'filename': filename, **metadata})
                LOGGER.info('file saved : %s', filename)
            else:
                LOGGER.info('already saved : %s', filename)
        return new_papers

    @task
    def regenerate_html(papers: list[dict]) -> list[dict]:
        path = write_html()
        LOGGER.info('html updated : %s', path)
        return papers

    @task(retries=1, retry_delay=timedelta(minutes=2))
    def send_notifications(papers: list[dict]) -> None:
        for paper in papers:
            notify_discord(paper)
        LOGGER.info('%d notifications sent', len(papers))

    send_notifications(regenerate_html(process_papers(scan_papers())))


research_paper_pipeline()
