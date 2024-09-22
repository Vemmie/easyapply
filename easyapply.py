import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd

# Function to scrape job data from Indeed based on user input
def scrape_jobs():
    job_title = job_title_entry.get().replace(" ", "+")
    zip_code = zip_code_entry.get()
    num_pages = int(pages_entry.get())
    
    if not job_title or not zip_code or not num_pages:
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    job_titles, companies, job_links = [], [], []
    
    for page in range(num_pages):
        url = f"https://www.indeed.com/jobs?q={job_title}&l={zip_code}&start={page * 10}"
        driver.get(url)
        time.sleep(3)
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "lxml")

        for job_card in soup.find_all("div", class_="job_seen_beacon"):
            title_elem = job_card.find("h2", class_="jobTitle")
            title = title_elem.text.strip() if title_elem else "No Title Found"
            job_titles.append(title)

            link_elem = job_card.find("a", class_="jcs-JobTitle")
            full_link = f"https://www.indeed.com{link_elem['href']}" if link_elem else "No Link Found"
            job_links.append(full_link)
    
    # Visit each job link to scrape company name
    for link in job_links:
        if link != "No Link Found":
            driver.get(link)
            time.sleep(3)
            job_page_source = driver.page_source
            job_soup = BeautifulSoup(job_page_source, "lxml")

            # Scrape company name
            company_elem = job_soup.find("div", {"data-testid": "inlineHeader-companyName"})
            if company_elem:
                company_name = company_elem.find("a").text.strip() if company_elem.find("a") else "No Company Found"
            else:
                company_name = "No Company Found"
            companies.append(company_name)
        else:
            companies.append("No Company Found")

    driver.quit()

    jobs_df = pd.DataFrame({
        "Job Title": job_titles,
        "Company": companies,
        "Job Link": job_links
    })
    
    jobs_df.to_csv("scraped_jobs.csv", index=False)
    messagebox.showinfo("Success", f"Scraping completed. Data saved to scraped_jobs.csv.")

# Create the GUI using Tkinter
root = tk.Tk()
root.title("Indeed Job Scraper")

# Job Title Entry
tk.Label(root, text="Job Title:").grid(row=0, column=0, padx=10, pady=10)
job_title_entry = tk.Entry(root, width=30)
job_title_entry.grid(row=0, column=1, padx=10, pady=10)

# ZIP Code Entry
tk.Label(root, text="ZIP Code:").grid(row=1, column=0, padx=10, pady=10)
zip_code_entry = tk.Entry(root, width=30)
zip_code_entry.grid(row=1, column=1, padx=10, pady=10)

# Number of Pages Entry
tk.Label(root, text="Number of Pages:").grid(row=2, column=0, padx=10, pady=10)
pages_entry = tk.Entry(root, width=30)
pages_entry.grid(row=2, column=1, padx=10, pady=10)

# Scrape Button
scrape_button = tk.Button(root, text="Scrape Jobs", command=scrape_jobs, bg="green", fg="white")
scrape_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Start the Tkinter main loop
root.mainloop()