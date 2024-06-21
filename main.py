from selenium import webdriver
import time
import bs4
from plyer import notification
import datetime
import colorama
from lib.logger import logging

BASE_URL = "http://10.10.0.1/scoreboard"

LOGGING_LEVEL = "INFO" #The logging level (if debug will displayed all log with level debug >=)

SERVICES = { #The service with relative index (The indices refer to the order on the scoreboard from the left)
        5: "WeirdCPU",
        4: "SaaS",
        3: "NotABook - 2",
        2: "NotABook - 1",
        1: "CTFe - 2",
        0: "CTFe - 1",
    }

TARGETS = ["Università degli Studi di Salerno"] #The universities that will be monitored (if the value is None, all universities will be displayed)
    
RELOAD = 10 # After how many seconds the control is repeated

class SLANotifier:
    
    def __init__(self,services,target_team=None): 
        self.services = services
        self.target_team = target_team
        self.notified = False
        options = webdriver.ChromeOptions()
        options.add_argument('headless')  
        self.driver = webdriver.Chrome(options=options)

    def fetch_page_source(self,url):
        logging.info("Opening the browser")
        self.driver.get(url)
        logging.info("Loading content")
        time.sleep(2) 
        logging.info("Content loaded")
        return self.driver.page_source

    def parse_teams_data(self,html):
        logging.debug("Getting teams data")
        
        soup = bs4.BeautifulSoup(html, 'html.parser')
        teams_data = []
        tr_tags = soup.find_all('tr')
        
        logging.info(f"Found {len(tr_tags)} teams")

        if(len(tr_tags) == 0):
            return 404
    
        for index, tr in enumerate(tr_tags):
            service_td = tr.find_all('td', class_="px-1 align-start text-start")
            team_name_spans = tr.find_all('span', class_='fw-bold')
            score_td = tr.find_all('td', class_='px-1 align-middle')
            
            team_names = [span.text for span in team_name_spans]
            
            if(not any(target in team_names for target in self.target_team) and self.target_team != None):
                continue
            
            scores = [td.text.strip() for td in score_td]

            stats_info = self.parse_service_stats(service_td)

            teams_data.append({
                "name": team_names,
                "index": index,
                "score": scores,
                "stats_service": stats_info
            })

        return teams_data

    def parse_service_stats(self,service_td):
        logging.debug("Getting service data")
        stats_info = []
        for index_service, service in enumerate(service_td):
            stats = service.find_all("div", class_="d-flex")
            isDown = any(button for button in service.find_all("button", class_="btn-danger"))

            score_service = [div.text.strip() for div in stats]
            
            stats_info.append({
                'name': self.services[index_service],
                'score_service': score_service[0],
                'flag_attack': score_service[1],
                'flag_stolen': score_service[2],
                'status': score_service[3],
                'down': isDown
            })
        return stats_info

    def send_notify(self,data):
        logging.info("Controlling the service...")
        flag_c = False
        down_services = []
        for team in data:
            for service in team['stats_service']:
                if(service['down']):
                    flag_c = True
                    if(not self.notified):
                        notification.notify(
                            title='Alert',
                            message=f'The service: {service["name"]} is down for target {team["name"][0]} | {datetime.datetime.now().strftime("%H:%M:%S")}',
                            timeout=10
                        )
                        logging.info(f'Notification sent for service {service["name"]} in team {team["name"][0]}.')
                    down_services.append(service['name'])

        if(flag_c):
            self.notified = True
            logging.warning(f"Some service are down: {down_services}")
        else:
            self.notified = False
            logging.info(f'All service are UP.')

        logging.info("Control ended!")    
    
    def run(self,repeat_after:int):
        logging.info("Starting the script...")
        logging.info("Ctrl-C for exit the execution")
        exec_count = 0
        
        logging.debug(f"Services {self.services}")
        logging.debug(f"Targets {self.target_team}")

        while(True):
            exec_count += 1
            logging.info(f"Number of execution: {exec_count}")
            html = self.fetch_page_source(BASE_URL)
            teams_data = self.parse_teams_data(html)    
            
            if(teams_data != 404):
                self.send_notify(teams_data)
            else:
                logging.error("An error occurred in fetch of page")
            
            logging.debug(teams_data)
            time.sleep(repeat_after)

if __name__ == '__main__':
    # All parameters on top
    colorama.init(autoreset=True)
    
    notification.notify(
            title='Check notification',
            message=f'This notification is only for check the notification system',
            timeout=10
    )
    
    sla = SLANotifier(SERVICES,TARGETS)
    sla.run(RELOAD)
    
#@akiidjk
