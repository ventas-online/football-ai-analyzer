import csv
from io import StringIO
from urllib.request import urlopen

BASE='https://www.football-data.co.uk/mmz4281/{season}/E0.csv'

def load_season_odds(season: str):
    with urlopen(BASE.format(season=season), timeout=30) as r:
        text=r.read().decode('latin-1')
    rows=list(csv.DictReader(StringIO(text)))
    out=[]
    for x in rows:
        try:
            date=x.get('Date','').strip()
            home=x.get('HomeTeam','').strip(); away=x.get('AwayTeam','').strip()
            fthg=int(float(x['FTHG'])); ftag=int(float(x['FTAG']))
            for market,col in [('home','AvgH'),('draw','AvgD'),('away','AvgA'),('over_2_5','Avg>2.5'),('under_2_5','Avg<2.5')]:
                if x.get(col): out.append({'date':date,'home_team':home,'away_team':away,'market':market,'market_odds':float(x[col]),'won': int((market=='home' and fthg>ftag) or (market=='draw' and fthg==ftag) or (market=='away' and fthg<ftag) or (market=='over_2_5' and fthg+ftag>2) or (market=='under_2_5' and fthg+ftag<3))})
        except (ValueError,TypeError,KeyError):
            continue
    return out
