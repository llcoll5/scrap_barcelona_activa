import requests

def get_jobs_from_api(url):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        jobs = response.json()
        return jobs['jobs'].values()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

if __name__ == "__main__":
    url = "https://api.talentclue.com/jswidget-ajax/jswidget/jobs/e95d473e3656ff3751a99ec859c42454"
    jobs = get_jobs_from_api(url)
    if jobs:
        for job in jobs:
            # print(job)
            print(f"Title: {job['title']}, Link: {job['url']}")
    else:
        print("No jobs found or error occurred.")