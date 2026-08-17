import os
import uuid
from loguru import logger

async def auto_apply_copilot(job_url: str, user_name: str, user_email: str, cover_letter: str) -> str:
    """
    Phase 7: Playwright-based auto-apply copilot.
    Navigates to the job URL, attempts to fill in basic fields, 
    and takes a screenshot for human review.
    Does NOT submit the form (respects ToS / human-in-the-loop).
    Returns the URL path to the screenshot.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.error("Playwright not installed. Ensure it is uncommented in requirements.txt.")
        return ""

    logger.info(f"Starting auto-apply copilot for {job_url}")
    
    # Ensure screenshots dir exists so we can serve them statically
    os.makedirs("static/screenshots", exist_ok=True)
    filename = f"auto_apply_{uuid.uuid4().hex[:8]}.png"
    screenshot_path = f"static/screenshots/{filename}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            await page.goto(job_url, wait_until="domcontentloaded", timeout=30000)
            
            # Simple heuristic form filling (Best effort)
            
            # 1. Name
            name_inputs = await page.query_selector_all('input[name*="name" i], input[id*="name" i]')
            if name_inputs:
                await name_inputs[0].fill(user_name)
                
            # 2. Email
            email_inputs = await page.query_selector_all('input[type="email"], input[name*="email" i]')
            if email_inputs:
                await email_inputs[0].fill(user_email)
                
            # 3. Cover Letter (Textarea)
            textareas = await page.query_selector_all('textarea[name*="cover" i], textarea[id*="cover" i], textarea')
            if textareas and cover_letter:
                await textareas[0].fill(cover_letter)
                
            # Take a screenshot to show the user what we filled
            await page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"Auto-apply screenshot saved to {screenshot_path}")
            
        except Exception as e:
            logger.error(f"Error during auto-apply navigation: {e}")
            # Try to grab a screenshot of the error state
            await page.screenshot(path=screenshot_path)
            
        finally:
            await browser.close()
            
    # Return the URL path relative to the domain (served via FastAPI static files)
    return f"/app/screenshots/{filename}"
