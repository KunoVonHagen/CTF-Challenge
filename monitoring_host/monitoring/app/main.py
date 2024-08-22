import asyncio
import time
from playwright.async_api import async_playwright
import requests
from http.client import responses
from datetime import datetime, timedelta
import hashlib
import os
import sys

monitoring_interval_seconds = int(os.getenv('MONITORING_INTERVAL_SECONDS'))
monitoring_session_secret = os.getenv('MONITORING_SESSION_SECRET')
monitoring_session = hashlib.md5(monitoring_session_secret.encode()).hexdigest()

# Calculate a far-future expiration date
expires_at = datetime.utcnow() + timedelta(days=365*10)  # 10 years in the future

# Convert to timestamp
expires_timestamp = int(expires_at.timestamp())

# Base URL
website_host = 'ctf-challenge.edu'
website_port = 8080

url = f"http://{website_host}:{website_port}"

# Pages to check
check_pages = [{'url': f'', 'title': 'Index'},
               {'url': f'/admin', 'title': 'Admin'},
               {'url': f'/login', 'title': 'Login'},
               {'url': f'/status', 'title': 'Status'},
               {'url': f'/monitoring-test', 'title': 'Monitoring Test (switches between 200, 403, 404)'}]

async def main():
    async with async_playwright() as p:
        # Launch a headless browser
        browser = await p.chromium.launch(headless=True)
        
        context = await browser.new_context()
                
        await context.add_cookies([{
            'name': 'session',
            'value': monitoring_session,
            'domain': website_host,
            'path': '/',
            'httpOnly': False,
            'secure': False
        }])
        
        page = await context.new_page()
        
        # Monitoring service
        while True:
            last_update_start = time.time()

            for page_info in check_pages:
                response = await page.goto(url + page_info['url'])
                await page.wait_for_load_state('networkidle')  # Wait for the page to load completely
                
                cookies = await context.cookies()
                #print("Cookies:", cookies)

                #print(response.status, page_info['url'])

                # Build status dictionary
                status = {
                    'title': page_info['title'],
                    'url': page_info['url'].replace(url, ""),
                    'code': response.status,
                    'description': responses[response.status]
                }

                #print(status)

                # Post the status update
                await page.request.post(f'{url}/update-status', data={'status_update': status})

            # Sleep 10 seconds before the next update
            await asyncio.sleep(max(monitoring_interval_seconds - (time.time() - last_update_start), 0))


if __name__ == '__main__':
    asyncio.run(main())
