import aiohttp, asyncio, time, requests as r
from colorama import Fore, init
init()



def get_zones():
    url = "https://www.thewindpower.net/country_zones_en_27_poland.php"
    links = []
    for i in range(1195, 1211):
        url = f"https://www.thewindpower.net/zones_en_27_{i}.php"
        links.append(url)
    return links

async def async_get_farms(s, url):
    farms = []
    result = await s.get(url)
    # print(result.status_code, url,  "\n")
    text = await result.text()
    text = text.split('<td style="width:50%;" class="entete_tableau"><b>Name</b></td>')[1]
    text = text.split('href="windfarm_en_')
    text.pop(0)
    
    for e in text:
        link = e.split('">')[0]
        link = "https://www.thewindpower.net/" + "windfarm_en_" + link
        farms.append(link)
    return farms

async def async_get_values(s, url):
    result = await s.get(url)
    text = await result.text()
    text = text.split("<h1>Details</h1>")[1]
    text = text.split("<h1>Localisation</h1>")[0]
    text = text.split("Total nominal power: ")
    text.pop(0)
    value = 0
    for _t in text:
        value = value + float(_t.split(" ")[0].replace(",", "."))
    return f'"{url.split("_")[-1].split(".")[0]}": {value}'
        
        
async def main():
    t_s = time.time()
    print(f"{Fore.YELLOW}Getting zones...")
    zones = get_zones()
    print(f"{Fore.GREEN}DONE in {round(time.time()-t_s, 2)}s\n")
    t_s = time.time()
    print(f"{Fore.YELLOW}Getting farms...")
    async with aiohttp.ClientSession() as s:
        result = await asyncio.gather(*(async_get_farms(s, zone) for zone in zones))
    farms = []
    for farm in result:
        farms = farms + farm
    print(f"{Fore.GREEN}DONE in {round(time.time()-t_s, 2)}s\n")
    
    t_s = time.time()
    print(f"{Fore.YELLOW}Getting values...")
    with open("data.json", "w") as f:
        f.write("{\n") 
    async with aiohttp.ClientSession() as s:
        result = await asyncio.gather(*(async_get_values(s, farm) for farm in farms))
    with open("data.json", "a") as d:
        l = len(result)-1
        for index, row in enumerate(result):
            if index == l:
                d.write(f"{row}\n")
            else:
                d.write(f"{row},\n")
        d.write("}")
    print(f"{Fore.GREEN}DONE in {round(time.time()-t_s, 2)}s\n{Fore.RESET}")



loop = asyncio.get_event_loop()
loop.run_until_complete(main())