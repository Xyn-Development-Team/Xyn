import requests
from bs4 import BeautifulSoup

currency_language_mapping = {
    'AED': 'ar-AE',  # United Arab Emirates Dirham - Arabic (United Arab Emirates)
    'AFN': 'ps-AF',  # Afghan Afghani - Pashto (Afghanistan)
    'ALL': 'sq-AL',  # Albanian Lek - Albanian (Albania)
    'AMD': 'hy-AM',  # Armenian Dram - Armenian (Armenia)
    'ANG': 'nl-AN',  # Netherlands Antillean Guilder - Dutch (Netherlands Antilles)
    'AOA': 'pt-AO',  # Angolan Kwanza - Portuguese (Angola)
    'ARS': 'es-AR',  # Argentine Peso - Spanish (Argentina)
    'AUD': 'en-AU',  # Australian Dollar - English (Australia)
    'AWG': 'nl-AW',  # Aruban Florin - Dutch (Aruba)
    'AZN': 'az-AZ',  # Azerbaijani Manat - Azerbaijani (Azerbaijan)
    'BAM': 'bs-BA',  # Bosnia-Herzegovina Convertible Mark - Bosnian (Bosnia and Herzegovina)
    'BBD': 'en-BB',  # Barbadian Dollar - English (Barbados)
    'BDT': 'bn-BD',  # Bangladeshi Taka - Bengali (Bangladesh)
    'BGN': 'bg-BG',  # Bulgarian Lev - Bulgarian (Bulgaria)
    'BHD': 'ar-BH',  # Bahraini Dinar - Arabic (Bahrain)
    'BIF': 'fr-BI',  # Burundian Franc - French (Burundi)
    'BMD': 'en-BM',  # Bermudan Dollar - English (Bermuda)
    'BND': 'ms-BN',  # Brunei Dollar - Malay (Brunei Darussalam)
    'BOB': 'es-BO',  # Bolivian Boliviano - Spanish (Bolivia)
    'BRL': 'pt-BR',  # Brazilian Real - Portuguese (Brazil)
    'BSD': 'en-BS',  # Bahamian Dollar - English (Bahamas)
    'BTN': 'dz-BT',  # Bhutanese Ngultrum - Dzongkha (Bhutan)
    'BWP': 'en-BW',  # Botswanan Pula - English (Botswana)
    'BYN': 'be-BY',  # Belarusian Ruble - Belarusian (Belarus)
    'BZD': 'en-BZ',  # Belize Dollar - English (Belize)
    'CAD': 'en-CA',  # Canadian Dollar - English (Canada)
    'CDF': 'fr-CD',  # Congolese Franc - French (Democratic Republic of the Congo)
    'CHF': 'de-CH',  # Swiss Franc - German (Switzerland)
    'CLP': 'es-CL',  # Chilean Peso - Spanish (Chile)
    'CNY': 'zh-CN',  # Chinese Yuan - Chinese (China)
    'COP': 'es-CO',  # Colombian Peso - Spanish (Colombia)
    'CRC': 'es-CR',  # Costa Rican Colón - Spanish (Costa Rica)
    'CUC': 'es-CU',  # Cuban Convertible Peso - Spanish (Cuba)
    'CUP': 'es-CU',  # Cuban Peso - Spanish (Cuba)
    'CVE': 'pt-CV',  # Cape Verdean Escudo - Portuguese (Cape Verde)
    'CZK': 'cs-CZ',  # Czech Koruna - Czech (Czech Republic)
    'DJF': 'fr-DJ',  # Djiboutian Franc - French (Djibouti)
    'DKK': 'da-DK',  # Danish Krone - Danish (Denmark)
    'DOP': 'es-DO',  # Dominican Peso - Spanish (Dominican Republic)
    'DZD': 'ar-DZ',  # Algerian Dinar - Arabic (Algeria)
    'EGP': 'ar-EG',  # Egyptian Pound - Arabic (Egypt)
    'ERN': 'ti-ER',  # Eritrean Nakfa - Tigrinya (Eritrea)
    'ETB': 'am-ET',  # Ethiopian Birr - Amharic (Ethiopia)
    'EUR': 'en-EU',  # Euro - English (European Union)
    'FJD': 'en-FJ',  # Fijian Dollar - English (Fiji)
    'FKP': 'en-FK',  # Falkland Islands Pound - English (Falkland Islands)
    'GBP': 'en-GB',  # British Pound - English (United Kingdom)
    'GEL': 'ka-GE',  # Georgian Lari - Georgian (Georgia)
    'GGP': 'en-GG',  # Guernsey Pound - English (Guernsey)
    'GHS': 'en-GH',  # Ghanaian Cedi - English (Ghana)
    'GIP': 'en-GI',  # Gibraltar Pound - English (Gibraltar)
    'GMD': 'en-GM',  # Gambian Dalasi - English (Gambia)
    'GNF': 'fr-GN',  # Guinean Franc - French (Guinea)
    'GTQ': 'es-GT',  # Guatemalan Quetzal - Spanish (Guatemala)
    'GYD': 'en-GY',  # Guyanaese Dollar - English (Guyana)
    'HKD': 'zh-HK',  # Hong Kong Dollar - Chinese (Hong Kong)
    'HNL': 'es-HN',  # Honduran Lempira - Spanish (Honduras)
    'HRK': 'hr-HR',  # Croatian Kuna - Croatian (Croatia)
    'HTG': 'ht-HT',  # Haitian Gourde - Haitian Creole (Haiti)
    'HUF': 'hu-HU',  # Hungarian Forint - Hungarian (Hungary)
    'IDR': 'id-ID',  # Indonesian Rupiah - Indonesian (Indonesia)
    'ILS': 'he-IL',  # Israeli Shekel - Hebrew (Israel)
    'IMP': 'en-IM',  # Manx Pound - English (Isle of Man)
    'INR': 'hi-IN',  # Indian Rupee - Hindi (India)
    'IQD': 'ar-IQ',  # Iraqi Dinar - Arabic (Iraq)
    'IRR': 'fa-IR',  # Iranian Rial - Persian (Iran)
    'ISK': 'is-IS',  # Icelandic Króna - Icelandic (Iceland)
    'JEP': 'en-JE',  # Jersey Pound - English (Jersey)
    'JMD': 'en-JM',  # Jamaican Dollar - English (Jamaica)
    'JOD': 'ar-JO',  # Jordanian Dinar - Arabic (Jordan)
    'JPY': 'ja-JP',  # Japanese Yen - Japanese (Japan)
    'KES': 'sw-KE',  # Kenyan Shilling - Swahili (Kenya)
    'KGS': 'ky-KG',  # Kyrgyzstani Som - Kyrgyz (Kyrgyzstan)
    'KHR': 'km-KH',  # Cambodian Riel - Khmer (Cambodia)
    'KMF': 'ar-KM',  # Comorian Franc - Arabic (Comoros)
    'KPW': 'ko-KP',  # North Korean Won - Korean (North Korea)
    'KRW': 'ko-KR',  # South Korean Won - Korean (South Korea)
    'KWD': 'ar-KW',  # Kuwaiti Dinar - Arabic (Kuwait)
    'KYD': 'en-KY',  # Cayman Islands Dollar - English (Cayman Islands)
    'KZT': 'kk-KZ',  # Kazakhstani Tenge - Kazakh (Kazakhstan)
    'LAK': 'lo-LA',  # Laotian Kip - Lao (Laos)
    'LBP': 'ar-LB',  # Lebanese Pound - Arabic (Lebanon)
    'LKR': 'si-LK',  # Sri Lankan Rupee - Sinhala (Sri Lanka)
    'LRD': 'en-LR',  # Liberian Dollar - English (Liberia)
    'LSL': 'en-LS',  # Lesotho Loti - English (Lesotho)
    'LYD': 'ar-LY',  # Libyan Dinar - Arabic (Libya)
    'MAD': 'ar-MA',  # Moroccan Dirham - Arabic (Morocco)
    'MDL': 'ro-MD',  # Moldovan Leu - Romanian (Moldova)
    'MGA': 'mg-MG',  # Malagasy Ariary - Malagasy (Madagascar)
    'MKD': 'mk-MK',  # Macedonian Denar - Macedonian (North Macedonia)
    'MMK': 'my-MM',  # Myanma Kyat - Burmese (Myanmar)
    'MNT': 'mn-MN',  # Mongolian Tögrög - Mongolian (Mongolia)
    'MOP': 'zh-MO',  # Macanese Pataca - Chinese (Macau)
    'MRO': 'ar-MR',  # Mauritanian Ouguiya - Arabic (Mauritania)
    'MUR': 'en-MU',  # Mauritian Rupee - English (Mauritius)
    'MVR': 'dv-MV',  # Maldivian Rufiyaa - Divehi (Maldives)
    'MWK': 'ny-MW',  # Malawian Kwacha - Chichewa (Malawi)
    'MXN': 'es-MX',  # Mexican Peso - Spanish (Mexico)
    'MYR': 'ms-MY',  # Malaysian Ringgit - Malay (Malaysia)
    'MZN': 'pt-MZ',  # Mozambican Metical - Portuguese (Mozambique)
    'NAD': 'en-NA',  # Namibian Dollar - English (Namibia)
    'NGN': 'en-NG',  # Nigerian Naira - English (Nigeria)
    'NIO': 'es-NI',  # Nicaraguan Córdoba - Spanish (Nicaragua)
    'NOK': 'no-NO',  # Norwegian Krone - Norwegian (Norway)
    'NPR': 'ne-NP',  # Nepalese Rupee - Nepali (Nepal)
    'NZD': 'en-NZ',  # New Zealand Dollar - English (New Zealand)
    'OMR': 'ar-OM',  # Omani Rial - Arabic (Oman)
    'PAB': 'es-PA',  # Panamanian Balboa - Spanish (Panama)
    'PEN': 'es-PE',  # Peruvian Sol - Spanish (Peru)
    'PGK': 'en-PG',  # Papua New Guinean Kina - English (Papua New Guinea)
    'PHP': 'fil-PH',  # Philippine Peso - Filipino (Philippines)
    'PKR': 'ur-PK',  # Pakistani Rupee - Urdu (Pakistan)
    'PLN': 'pl-PL',  # Polish Złoty - Polish (Poland)
    'PYG': 'es-PY',  # Paraguayan Guarani - Spanish (Paraguay)
    'QAR': 'ar-QA',  # Qatari Riyal - Arabic (Qatar)
    'RON': 'ro-RO',  # Romanian Leu - Romanian (Romania)
    'RSD': 'sr-RS',  # Serbian Dinar - Serbian (Serbia)
    'RUB': 'ru-RU',  # Russian Ruble - Russian (Russia)
    'RWF': 'rw-RW',  # Rwandan Franc - Kinyarwanda (Rwanda)
    'SAR': 'ar-SA',  # Saudi Riyal - Arabic (Saudi Arabia)
    'SBD': 'en-SB',  # Solomon Islands Dollar - English (Solomon Islands)
    'SCR': 'en-SC',  # Seychellois Rupee - English (Seychelles)
    'SDG': 'ar-SD',  # Sudanese Pound - Arabic (Sudan)
    'SEK': 'sv-SE',  # Swedish Krona - Swedish (Sweden)
    'SGD': 'en-SG',  # Singapore Dollar - English (Singapore)
    'SHP': 'en-SH',  # Saint Helena Pound - English (Saint Helena)
    'SLL': 'en-SL',  # Sierra Leonean Leone - English (Sierra Leone)
    'SOS': 'so-SO',  # Somali Shilling - Somali (Somalia)
    'SRD': 'nl-SR',  # Surinamese Dollar - Dutch (Suriname)
    'SSP': 'en-SS',  # South Sudanese Pound - English (South Sudan)
    'STD': 'pt-ST',  # São Tomé and Príncipe Dobra - Portuguese (São Tomé and Príncipe)
    'SVC': 'es-SV',  # Salvadoran Colón - Spanish (El Salvador)
    'SYP': 'ar-SY',  # Syrian Pound - Arabic (Syria)
    'SZL': 'en-SZ',  # Eswatini Lilangeni - English (Eswatini)
    'THB': 'th-TH',  # Thai Baht - Thai (Thailand)
    'TJS': 'tg-TJ',  # Tajikistani Somoni - Tajik (Tajikistan)
    'TMT': 'tk-TM',  # Turkmenistan Manat - Turkmen (Turkmenistan)
    'TND': 'ar-TN',  # Tunisian Dinar - Arabic (Tunisia)
    'TOP': 'to-TO',  # Tongan Pa'anga - Tongan (Tonga)
    'TRY': 'tr-TR',  # Turkish Lira - Turkish (Turkey)
    'TTD': 'en-TT',  # Trinidad and Tobago Dollar - English (Trinidad and Tobago)
    'TWD': 'zh-TW',  # New Taiwan Dollar - Chinese (Taiwan)
    'TZS': 'sw-TZ',  # Tanzanian Shilling - Swahili (Tanzania)
    'UAH': 'uk-UA',  # Ukrainian Hryvnia - Ukrainian (Ukraine)
    'UGX': 'sw-UG',  # Ugandan Shilling - Swahili (Uganda)
    'USD': 'en-US',  # United States Dollar - English (United States)
    'UYU': 'es-UY',  # Uruguayan Peso - Spanish (Uruguay)
    'UZS': 'uz-UZ',  # Uzbekistan Som - Uzbek (Uzbekistan)
    'VEF': 'es-VE',  # Venezuelan Bolívar - Spanish (Venezuela)
    'VND': 'vi-VN',  # Vietnamese Đồng - Vietnamese (Vietnam)
    'VUV': 'bi-VU',  # Vanuatu Vatu - Bislama (Vanuatu)
    'WST': 'sm-WS',  # Samoan Tala - Samoan (Samoa)
    'XAF': 'fr-XF',  # Central African CFA Franc - French (Central African Republic, Chad, Congo, Equatorial Guinea, Gabon)
    'XCD': 'en-XC',  # East Caribbean Dollar - English (Anguilla, Antigua and Barbuda, Dominica, Grenada, Montserrat, Saint Kitts and Nevis, Saint Lucia, Saint Vincent and the Grenadines)
    'XOF': 'fr-XO',  # West African CFA Franc - French (Benin, Burkina Faso, Côte d'Ivoire, Guinea-Bissau, Mali, Niger, Senegal, Togo)
    'XPF': 'fr-XF',  # CFP Franc - French (French Polynesia, New Caledonia, Wallis and Futuna)
    'YER': 'ar-YE',  # Yemeni Rial - Arabic (Yemen)
    'ZAR': 'en-ZA',  # South African Rand - English (South Africa)
    'ZMW': 'en-ZM',  # Zambian Kwacha - English (Zambia)
    'ZWL': 'en-ZW',  # Zimbabwean Dollar - English (Zimbabwe)
}

def search_game(query):
    url = f"https://store.steampowered.com/search/?term={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    search_results = soup.find_all('a', class_='search_result_row')
    if search_results:
        first_result = search_results[0]
        app_id = first_result['data-ds-appid']
        return app_id
    else:
        return None

def profile(id=str):
    """### Returns info about a specified user
    `id`: SteamID for that user, not username!"""
    
    url = f"https://steamcommunity.com/id/{id}/"
    friends_url = f"https://steamcommunity.com/id/{id}/friends/"

    response = requests.get(url)
    friends_response = requests.get(url)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    friends_soup = BeautifulSoup(friends_response.content, 'html.parser')
    
    user = {
        "pfp": None, #/
        "username": None, #/
        "summary": None, #/
        "level": None, #/
        "status": None, #/
        "friend_count": None,
    }
    
    user["pfp"] = soup.find('div',{'class':'playerAvatarAutoSizeInner'}).find("img")["src"]
    
    user["username"] = soup.find('span',{'class':'actual_persona_name'}).get_text()
    
    user["summary"] = soup.find('div',{'class':'profile_summary'}).get_text().strip()
    
    user["level"] = soup.find('span',{'class':'friendPlayerLevelNum'}).get_text()
    
    user["status"] = str(soup.find('div',{'class':'profile_in_game_header'}).get_text()).replace("Currently ","")
    
    user["friend_count"] = soup.find_all('span',{'class':'profile_count_link_total'})[-1].get_text().strip()
    
    return user
    
    

def game(app_id=None,currency=None,name=str):
    """### Returns info about a game specified in the parameters
    `app_id`: Steam's game ID to get info from\n
    `currency`: Currency code for the price\n
    `name`: Game's name for searchfor """

    if not currency:
        currency = "USD"

    #Game URL
    url = f"https://store.steampowered.com/app/{app_id if app_id else search_game(name)}/"

    game ={
        "title": None, #/
        "price": None, #/
        "description": None, #/
        "banner": None, #/
        "game_url": url, #/
        "developer": None, #/
        "developer_url": None, #/
        "publisher": None, #/
        "publisher_url": None, #/
        "genre": None, #/
        "genre_url": None, #/
        "franchise": None, #/
        "release_date": None, #/
        "recent_reviews_summary": None, #/
        "all_reviews_summary": None, #/
        }

    ## Price
    #Sets the currency to the currency code
    language_code = currency_language_mapping.get(currency)
    params = {"cc":f"{language_code.split('-')[1]}"}
    
    #Does the request
    response = requests.get(url,params=params)

    #Searches for the price
    soup = BeautifulSoup(response.content, 'html.parser')
    price_div = soup.find('div', class_='game_purchase_price')
    discounted_price_div = soup.find('div',class_='discount_final_price')
    
    if price_div:
        game["price"] = price_div.get_text(strip=True)
    elif discounted_price_div:
        game["price"] = discounted_price_div.get_text(strip=True) 

    try:
        ## Title
        game["title"] = soup.find("div",{"id":"appHubAppName","class":"apphub_AppName"}).get_text()
    except:
        return None

    ## Banner
    game["banner"] = soup.find('img', class_='game_header_image_full').get("src")

    ## Description
    game["description"] = soup.find('div',{"class":"game_description_snippet"}).get_text()

    ## Developer & Publisher
    game["developer_url"] = soup.find("div",{"class":"summary column","id":"developers_list"}).find("a")["href"]
    game["developer"] = str(soup.find_all("div",{"class":"summary column"})[2].get_text()).replace("\n","")
    
    game["publisher"] = str(soup.find_all("div",{"class":"summary column"})[3].get_text()).replace("\n","")
    game["publisher_url"] = soup.find_all("div",{"class":"summary column"})[3].find("a")["href"]

    ## Genre
    element = soup.find("span", {"data-panel": '{"flow-children":"row"}'})
    game["genre"] = element.text
    game["genre_url"] = element.find("a")["href"]

    ## Franchise
    try:
        franchise = str(soup.find_all("div",{"class":"dev_row"})[4].get_text()).replace("\n","")
        game["franchise"] = franchise.replace("Franchise:","")
    except IndexError:
        pass

    ## Release Date
    game["release_date"] = str(soup.find("div",{"class":"date"}).get_text())

    ## Recent reviews summary
    game["recent_reviews_summary"] = str(soup.find("span",{"class":"game_review_summary"}).get_text())
    
    ## All reviews summary
    game["all_reviews_summary"] = str(soup.find_all("span",{"class":"game_review_summary"})[1].get_text())

    return game

#Examples
if __name__ == "__main__":
    print(profile(id="dorkreamer"))
    print(profile(id="whipv"))
    print(game(app_id="1091500",currency="CAD"))