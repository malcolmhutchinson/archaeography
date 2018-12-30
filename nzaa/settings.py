"""Settings for the NZAA application. These import the home settings.


List of NZAA file region names and grid sheet identifiers in
NZAA_REGION_SHEETS from Smith, I.W.G.; (1994) Organisation and
operation of the New Zealand Archaeological Association site recording
scheme in Archaeology in New Zealand Volume 37 Number 4: December
1994.

"""

import os
from home.settings import *

BASE_URL = '/nzaa/'
BASE_FILESPACE = os.path.join(STATICFILES_DIRS[0], 'nzaa/')
LOGIN_PAGE = 'https://archsite.eaglegis.co.nz/NZAA/Account/Login/'
SITE_PAGE = "https://archsite.eaglegis.co.nz/NZAA/Site/?id="
EDIT_SITE = "https://archsite.eaglegis.co.nz/NZAA/Site/Edit/?id="
CREATE_SITE = "https://archsite.eaglegis.co.nz/NZAA/Site/Create"

CONDITION = (
    'Destroyed',
    'Not a site',
    'Unknown',
)

ETHNICITY = (
    'British',
    'Chinese',
    'Colonial',
    'European',
    'Maori',
    'Modern NZ',
    'Other',
    'Pakeha',
    'Polynesian',
)

NZAA_REGION_SHEETS = {
    'aucklandfile': (
        'P09',
        'Q09', 'Q10', 'Q11', 'Q12',
        'R09', 'R10', 'R11', 'R12',
        'S08', 'S11', 'S12',
        'T08', 'T09',
    ),
    'bayofplentyfile': (
        'U14', 'U15', 'U16',
        'V14', 'V15', 'V16', 'V17', 'V18',
        'W13', 'W14', 'W15', 'W16', 'W17',
        'X14', 'X15', 'X16',

    ),
    'canterburyfile': (
        'H37', 'H38', 'H39',
        'I36', 'I37', 'I38', 'I39',
        'J35', 'J36', 'J37', 'J38', 'J39', 'J40',
        'K34', 'K35', 'K36', 'K37', 'K38', 'K39',
        'L33', 'L34', 'L35', 'L36', 'L37',
        'M31', 'M32', 'M33', 'M34', 'M35', 'M36', 'M37',
        'N32', 'N33', 'N34',
        'O32', 'O33',
    ),
    'centralotagofile': (
        'E40', 'E41',
        'F39', 'F40', 'F41',
        'G39', 'G40', 'G41', 'G42',
        'H40', 'H41', 'H42',
    ),
    'coromandelfile': (
        'S09', 'S10', 'T10', 'T11', 'T12', 'T13',
        'U10', 'U11', 'U12', 'U13',
    ),
    'eastcoastfile': (
        'W18',
        'X17', 'X18', 'X19', 'X20',
        'Y14', 'Y15', 'Y16', 'Y17', 'Y18', 'Y19', 'Y20',
        'Z14', 'Z15', 'Z16', 'Z17',
    ),
    'hawkesbayfile': (
        'U22', 'U23', 'U24', 'U25',
        'V19', 'V20', 'V21', 'V22', 'V23', 'V24',
        'W19', 'W20', 'W21', 'W22',
    ),
    'marlboroughfile': (
        'M30',
        'N29', 'N30', 'N31',
        'O28', 'O29', 'O30', 'O31',
        'P27', 'P28', 'P29', 'P30', 'P31',
        'Q29',
    ),
    'nelsonfile': (
        'L25',
        'M24', 'M25', 'M26', 'M27', 'M28', 'M29',
        'N24', 'N25', 'N26', 'N27', 'N28',
        'O26', 'O27', 'P25', 'P26', 'Q26',
    ),
    'northlandfile': (
        'L01', 'M02', 'N02', 'N03', 'N04', 'N05',
        'O03', 'O04', 'O05', 'O06', 'O07',
        'P04', 'P05', 'P06', 'P07', 'P08',
        'Q04', 'Q05', 'Q06', 'Q07', 'Q08',
        'R06', 'R07', 'R08', 'S07',
    ),
    'otagofile': (
        'G43', 'G44',
        'H43', 'H44', 'H45', 'H46', 'H47',
        'I40', 'I41', 'I42', 'I43', 'I44', 'I45',
        'J41', 'J42', 'J43', 'J44',
    ),
    'pateafile': (
        'T19', 'T20', 'T21', 'T22',
        'U19', 'U20', 'U21',
    ),
    'southlandfile': (
        'A44', 'A45',
        'B41', 'B42', 'B43', 'B44', 'B45', 'B46', 'B47',
        'C40', 'C41', 'C42', 'C43', 'C44', 'C45', 'C46', 'C49', 'C50',
        'D39', 'D40', 'D41', 'D42', 'D43', 'D44',
        'D45', 'D46', 'D47', 'D48', 'D49', 'D50',
        'E42', 'E43', 'E44', 'E45', 'E46', 'E47', 'E48', 'E49',
        'F42', 'F43', 'F44', 'F45', 'F46', 'F47', 'F48',
        'G45', 'G46', 'G47',
    ),
    'taranakifile': (
        'P19', 'P20', 'P21',
        'Q18', 'Q19', 'Q20', 'Q21', 'Q22',
        'R18', 'R19', 'R20', 'R21',
    ),
    'taupofile': (
        'S18', 'T17', 'T18', 'U17', 'U18',
    ),
    'waikatofile': (
        'R13', 'R14', 'R15', 'R16', 'R17',
        'S13', 'S14', 'S15', 'S16', 'S17',
        'T14', 'T15', 'T16',
    ),
    'wanganuifile': (
        'R22', 'R23',
        'S19', 'S20', 'S21', 'S22', 'S23', 'S24',
        'T23', 'T24',
    ),
    'wellingtonfile': (
        'R25', 'R26', 'R27', 'R28', 'Q27',
        'S25', 'S26', 'S27', 'S28',
        'T25', 'T26', 'T27', 'T28',
        'U25', 'U26',
    ),
    'westcoastfile': (
        'D38',
        'E37', 'E38', 'E39',
        'F36', 'F37', 'F38',
        'G35', 'G36', 'G37', 'G38',
        'H34', 'H35', 'H36',
        'I33', 'I34', 'I35',
        'J31', 'J32', 'J33', 'J34',
        'K29', 'K30', 'K31', 'K32', 'K33',
        'L25', 'L26', 'L27', 'L28', 'L29', 'L30', 'L31', 'L32',
    ),
}

NZMS260 = (
    'A44', 'A45',

    'B41', 'B42', 'B43', 'B44', 'B45', 'B46', 'B47',

    'C40', 'C41', 'C42', 'C43', 'C44', 'C45', 'C46', 'C49',
    'C50',

    'D38', 'D39', 'D40', 'D41', 'D42', 'D43', 'D44', 'D45',
    'D46', 'D47', 'D48', 'D49', 'D50',

    'E37', 'E38', 'E39', 'E40', 'E41', 'E42', 'E43', 'E44',
    'E45', 'E46', 'E47', 'E48', 'E49',

    'F36', 'F37', 'F38', 'F39', 'F40', 'F41', 'F42', 'F43',
    'F44', 'F45', 'F46', 'F47', 'F48',

    'G35', 'G36', 'G37', 'G38', 'G39', 'G40', 'G41', 'G42',
    'G43', 'G44', 'G45', 'G46', 'G47',

    'H34', 'H35', 'H36', 'H37', 'H38', 'H39', 'H40', 'H41',
    'H42', 'H43', 'H44', 'H45', 'H46', 'H47',

    'I33', 'I34', 'I35', 'I36', 'I37', 'I38', 'I39', 'I40',
    'I41', 'I42', 'I43', 'I44', 'I45',

    'J31', 'J32', 'J33', 'J34', 'J35', 'J36', 'J37', 'J38',
    'J39', 'J40', 'J41', 'J42', 'J43', 'J44',

    'K29', 'K30', 'K31', 'K32', 'K33', 'K34', 'K35', 'K36',
    'K37', 'K38', 'K39',

    'L01', 'L25', 'L26', 'L27', 'L28', 'L29', 'L30', 'L31',
    'L32', 'L33', 'L34', 'L35', 'L36', 'L37',

    'M02', 'M24', 'M25', 'M26', 'M27', 'M28', 'M29', 'M30',
    'M31', 'M32', 'M33', 'M34', 'M35', 'M36', 'M37',

    'N02', 'N03', 'N04', 'N05', 'N24', 'N25', 'N26', 'N27',
    'N28', 'N29', 'N30', 'N31', 'N32', 'N33', 'N34', 'N36',
    'N37',

    'O03', 'O04', 'O05', 'O06', 'O07', 'O26', 'O27', 'O28',
    'O29', 'O30', 'O31', 'O32', 'O33',

    'P04', 'P05', 'P06', 'P07', 'P08', 'P09', 'P19', 'P20',
    'P21', 'P25', 'P26', 'P27', 'P28', 'P29', 'P30', 'P31',

    'Q04', 'Q05', 'Q06', 'Q07', 'Q08', 'Q09', 'Q10', 'Q11',
    'Q12', 'Q15', 'Q18', 'Q19', 'Q20', 'Q21', 'Q22', 'Q26',
    'Q27', 'Q29',

    'R06', 'R07', 'R08', 'R09', 'R10', 'R11', 'R12', 'R13',
    'R14', 'R15', 'R16', 'R17', 'R18', 'R19', 'R20', 'R21',
    'R22', 'R23', 'R25', 'R26', 'R27', 'R28',

    'S07', 'S08', 'S09', 'S10', 'S11', 'S12', 'S13', 'S14',
    'S15', 'S16', 'S17', 'S18', 'S19', 'S20', 'S21', 'S22',
    'S23', 'S24', 'S25', 'S26', 'S27', 'S28',

    'T08', 'T09', 'T10', 'T11', 'T12', 'T13', 'T14', 'T15',
    'T16', 'T17', 'T18', 'T19', 'T20', 'T21', 'T22', 'T23',
    'T24', 'T25', 'T26', 'T27', 'T28',

    'U10', 'U11', 'U12', 'U13', 'U14', 'U15', 'U16', 'U17',
    'U18', 'U19', 'U20', 'U21', 'U22', 'U23', 'U24', 'U25',
    'U26',

    'V14', 'V15', 'V16', 'V17', 'V18', 'V19', 'V20', 'V21',
    'V22', 'V23', 'V24',

    'W13', 'W14', 'W15', 'W16', 'W17', 'W18', 'W19', 'W20',
    'W21', 'W22',

    'X14', 'X15', 'X16', 'X17', 'X18', 'X19', 'X20',

    'Y14', 'Y15', 'Y16', 'Y17', 'Y18', 'Y19', 'Y20',

    'Z14', 'Z15', 'Z16', 'Z17',
)

OPSTATUS = (
    'Working',
    'Standing',
    'Completed',
)

PERIOD = (
    'Prehistoric',    # Up to European contact
    'Contact',        # European up to 1840
    'Colonial',       # 1840 - 1900
    'Historic',       # Combination of colonial, modern
    'Modern',         # 1900 - present
)
SEARCH_FIELDS = (
    'site_type',
    'subtype',
    'quality'
    'recorded_by',
    'affected_by',
    'features',
    'period',
    'ethnicity',
    'location',
)

SITE_TYPE = {
    'Administration': (
        'Cadastral',
        'Cairn',
        'Court House',
        'Fire service',
        'Gaol',
        'Government'
        'Land parcel',
        'Meeting place',
        'Memorial',
        'Museum',
        'Police',
        'Prison',
        'Survey mark',
        'Trig',
    ),
    'Agricultural': (
        'Accommodation',
        'Bridle track',
        'Building',
        'Bulldozer track',
        'Bullock track',
        'Cableway',
        'Causeway',
        'Cow shed',
        'Creamery',
        'Culvert',
        'Dairy',
        'Dam',
        'Drain',
        'Earthen fence',
        'Farm race',
        'Farm house',
        'Fence',
        'Pier',
        'Post',
        'Quarry',
        'Shearing shed',
        'Shed',
        'Stock bridge',
        'Stock race',
        'Stock yard',
        'Stone wall',
        'Structure',
        'Track',
        'Tramway',
        'Wall',
        'Water trough',
        'Well',
        'Wool shed',
        'Yard',
    ),
    'Art': (
        'Dendroglyph',
        'Petroglyph',
        'Rock art',
        'Scarred tree',
        'Stone carving',
    ),
    'Botanical': (
        'Cultivars',
        'Deciduous trees',
        'Exotic trees',
        'Forest clearing',
        'Fruit trees',
        'Grape vines',
        'Karaka',
        'Scarred tree',
        'Taro',
        'Trees',
    ),
    'Burial': (
        'Cemetery',
        'Cranium',
        'Dog',
        'Grave',
        'Urupa',
    ),
    'Cave/rock shelter': (
        'Cave',
        'Dwelling',
        'Rock shelter'
    ),
    'Community': (
        'Camp',
        'Church',
        'Hall',
        'Health',
        'Hospital',
        'Houses',
        'Institute',
        'Kainga',
        'Marae',
        'Mission station',
        'Monument',
        'Recreation',
        'Settlement',
        'Camp',
        'Town',
        'Village',
    ),
    'Commerce': (
        'Accommodation house',
        'Bakery',
        'Bank',
        'Blacksmith',
        'Bond store',
        'Bootmaker',
        'Bottle dump',
        'Brewery',
        'Building',
        'Butcher',
        'Dairy/creamery',
        'Dressmaker',
        'Grainstore',
        'Gumstore',
        'Hotel',
        'Ironmonger',
        'Malthouse',
        'Pharmacy',
        'Pier',
        'Shop',
        'Stables',
        'Stock yard',
        'Store',
        'Theatre',
        'Timber yard',
        'Trading station',
        'Warehouse',
        'Well',
    ),
    'Domestic': (
        'Artefact scatter',
        'Bach',
        'Bottle dump',
        'Camp',
        'Camp fire',
        'Clearing',
        'Cobbles',
        'Cob building',
        'Cottage',
        'Crib',
        'Dwelling',
        'Farmhouse',
        'Fireplace',
        'Hangi',
        'Homestead',
        'House',
        'Hut',
        'Kainga',
        'Occupation',
        'Path',
        'Pits',
        'Rubbish pit',
        'Settlement',
        'Stone scatter',
        'Terrace',
        'Well',
        'Whare',
    ),
    'Education': (
        'Gallery',
        'Library',
        'Museum',
        'School',
    ),
    'Find spot': (
        'Adze',
        'Cache',
        'Canoe',
        'Carving',
        'Flaking',
        'Greenstone',
        'Human remains',
        'Ko - digging stick',
        'Leather',
        'Moa bone',
        'Obsidian',
        'Wooden materials',
    ),
    'Fishing': (
        'Camp',
        'Eel weir',
        'Fish factory',
        'Fish trap',
        'Hatchery',
        'Patuna',
        'Stone traps',
        'Whare',
    ),
    'Forestry': (
        'Boiler',
        'Camp',
        'Dam',
        'Driving dam',
        'Forest Service hut',
        'Fire lookout',
        'Hauler'
        'Machinery',
        'Pier',
        'Quarry',
        'Road',
        'Saw mill',
        'Scarred tree',
        'Shed',
        'Track',
        'Tramway',
        'Tree stump',
    ),
    'Gum digging': (
        'Camp',
        'Dam',
        'Gum holes',
        'Hut',
    ),
    'Industry': (
        'Abbitoir',
        'Aqueduct',
        'Blacksmith',
        'Brickworks',
        'Brewery',
        'Camp',
        'Cannery',
        'Canoe building',
        'Cement works',
        'Cheese factory',
        'Culvert',
        'Dam',
        'Factory',
        'Forge',
        'Foundry',
        'Flax milling',
        'Flour milling',
        'Foundary',
        'Gasworks',
        'Hydro power',
        'Lime kiln',
        'Magazine',
        'Mill pond',
        'Pier',
        'Pipeline',
        'Portal',
        'Power plant',
        'Pumping station',
        'Quarry',
        'Race',
        'Shed',
        'Steeping pits',
        'Stone reduction',
        'Store',
        'Tannery',
        'Tramway',
        'Tunnel',
        'Viaduct',
        'Water race',
        'Water wheel',
    ),
    'Lithic working': (
        'Flakes',
        'Quarry',
        'Stone grooves',
    ),
    'Maori horticulture': (
        'Borrow pits',
        'Drainage system',
        'Field system',
        'Gardens',
        'Modified soils',
        'Stone piles',
        'Waikato valley horticulture',
    ),
    'Maritime': (
        'Blacksmith',
        'Camp',
        'Dockyards',
        'Hulk',
        'Jetty',
        'Mooring',
        'Pier',
        'Shipwreck',
        'Shipyard',
        'Shed',
        'Slipway',
        'Viaduct',
        'Whaling station',
        'Wharf',
    ),
    'Midden': (
        'Rubbish dump',
        'Rubbish heap',
        'Rubbish pit',

    ),
    'Midden/oven': (
        'Fireplace',
        'Hangi',
        'Oven',
        'Pit',
        'Shell midden',
        'Umu',
    ),
    'Military': (
        'Anti-aircraft battery',
        'Armed Constabulary blockhouse',
        'Armed Constabulary camp',
        'Armed Constabulary magazine',
        'Armed Constabulary redoubt',
        'Armed Constabulary stores',
        'Army camp',
        'Barracks',
        'Battle ground',
        'Blockhouse',
        'British Army redoubt',
        'Camp',
        'Coastal battery',
        'Commissariat',
        'Defensive structure',
        'Fortifications',
        'Gun emplacement',
        'Magazine',
        'Maori redoubt',
        'Minefield',
        'Observation post',
        'Pillbox',
        'Radar station',
        'Redoubt',
        'Rifle butts',
        'Rifle pits',
        'Sap',
        'Stockade',
        'Trench',
    ),
    'Mining': (
        'Adit',
        'Aerial way',
        'Antimony mine',
        'Aqueduct',
        'Asbestos',
        'Battery',
        'Blacksmith',
        'Cableway',
        'Camp',
        'Causeway',
        'Chromite',
        'Coal mine',
        'Copper/antimony',
        'Copper mine',
        'Crushing plant',
        'Culvert',
        'Dam',
        'Dredge',
        'Drive',
        'Dwelling',
        'Exploration',
        'Foundations',
        'Gold mine',
        'Hut',
        'Magazine',
        'Manganese mine',
        'Mercury mine',
        'Mica mine',
        'Mullock',
        'Oil',
        'Pier',
        'Power plant',
        'Prospecting',
        'Pumping station',
        'Quarry',
        'Race',
        'Road',
        'Scheelite',
        'Settlement',
        'Shaft',
        'Shed',
        'Slucing',
        'Stamper',
        'Stope',
        'Tailings',
        'Tin mine',
        'Town',
        'Tramway',
        'Viaduct',
        'Water race',
    ),
    'Mission station': (
        'Anglican',
        'Catholic',
        'CMS',
        'Methodist',
        'Wesleyan',
    ),
    'Not a site': (
        'Not a pa',
        'Not homestead',
        'Not terraces',
        'Not pits',
    ),
    'Pa': (
        'Cliff pa',
        'Gully pa',
        'Gunfighter pa',
        'Headland pa',
        'Hilltop pa',
        'Island pa',
        'Karst pa',
        'Lake pa',
        'Pa and urupa',
        'Promontory pa',
        'Ridge pa',
        'Ring-ditch pa',
        'River pa',
        'Spur-end pa',
        'Swamp pa',
        'Waikato gully pa',
        'Waikato river pa',
    ),
    'Pit/terrace': (
        'Midden',
        'Oven',
        'Pit',
        'Terrace',
    ),
    'Quarry': (
        'Argillite',
        'Basalt',
        'Chert',
        'Flint',
        'Greenstone',
        'Limestone',
        'Obsidian',
        'Ochre',
        'Silcrete',
    ),
    'Stone arrangement': (
        'Circular',
        'Linear',
        'Stone mound',
    ),
    # Sites recorded from hearsay or traditional knowledge.
    'Traditional site': (
        'Battle ground',
        'Camp',
        'Ceremonial site',
        'Fishing camp',
        'Kainga',
        'Landmark',
        'Marae',
        'Sacred tree',
        'Taniwha',
        'Village',
        'Whare',
    ),
    'Transport/communication': (
        'Aerial tramway',
        'Ballast',
        'Boat channel',
        'Bridge',
        'Bridge foundations',
        'Bridle track',
        'Bullock track',
        'Cable station',
        'Cableway',
        'Camp',
        'Causeway',
        'Coach road',
        'Cobbles',
        'Culvert',
        'Foot bridge',
        'Foot track',
        'Ford',
        'Jetty',
        'Landing',
        'Lighthouse',
        'Pier',
        'Quarry',
        'Railway',
        'Rail bridge',
        'Rail cutting',
        'Rail embankment',
        'Railway hut',
        'Rail station',
        'Rail tunnel',
        'Railway workshop',
        'Railyards',
        'Ramp',
        'River crossing',
        'Road',
        'Road bridge',
        'Road tunnel',
        'Rolling stock',
        'Shed',
        'Signal mast',
        'Signal station',
        'Suspension bridge',
        'Telegraph pole',
        'Track',
        'Tramway',
        'Tunnel',
        'Vehicle track',
        'Viaduct',
    ),
    'Trivial site': (
    ),
    'Unclassified': (
        'Unknown',
    ),
    'Whaling/sealing': (
        'Camp',
        'Sealing camp',
    ),
}

STATUS = (
    'Working',
    'Submitted',
    'Pending',
    'Approved',
    'Internal',
)
# REGION and TLA dictionaries should be construcuted in accordance
# with the principle of parsimony. The inclusion of 'region' or
# 'district' in the key should only be used to avoid ambiguity. Thus,
# 'waikatoregion' and 'waikatodistrict', but not 'ashbutrondistrict'
# or 'otagoregion'.

NZAA_REGION = {
    'aucklandfile': ('Auckland file', -36.9090, 174.8072, 9),
    'bayofplentyfile': ('Bay of Plenty file', -38.1466, 176.7593, 8),
    'canterburyfile': ('Canterbury file', -43.4717, 171.8629, 7),
    'centralotagofile': ('Central Otago file', -44.8602, 169.1856, 8),
    'coromandelfile': ('Coromandel file', -36.9695, 175.9020, 9),
    'eastcoastfile': ('East Coast file', -38.3694, 178.2849, 8),
    'hawkesbayfile': ("Hawke's Bay file", -39.6970, 176.5573, 9),
    'marlboroughfile': ('Marlborough file', -41.8694, 173.6469, 8),
    'nelsonfile': ('Nelson File', -41.1169, 173.1437, 8),
    'northlandfile': ('Northland file', -35.4273, 173.7876, 7),
    'otagofile': ('Otago file', -45.6513, 170.0942, 8),
    'pateafile': ('Inland Patea file', -39.3273, 176.0352, 9),
    'southlandfile': ('Southland file', -46.0537, 168.0144, 7),
    'taranakifile': ('Taranaki file', -39.3140, 174.3964, 9),
    'taupofile': ('Taupo file', -38.6319, 175.9754, 9),
    'waikatofile': ('Waikato file', -37.7846, 175.4797, 9),
    'wanganuifile': ('Wanganui file', -40.0044, 175.3592, 9),
    'wellingtonfile': ('Wellington file', -41.3160, 175.2241, 9),
    'westcoastfile': ('West Coast file', -43.1455, 169.6138, 6),
}

REGION = {
    "aucklandregion": ("Auckland Region", -37.7846, 175.2797, 10),
    "bayofplenty": ("Bay of Plenty Region", -37.7846, 175.2797, 13),
    "canterbury": ("Canterbury Region", -37.7846, 175.2797, 13),
    "gisborne": ("Gisborne", -37.7846, 175.2797, 13),
    "hawkesbay": ("Hawke's Bay Region", -37.7846, 175.2797, 13),
    "manawatuwanganui": ("Manawatu-Wanganui Region", -37.7846, 175.2797, 13),
    "marlboroughregion": ("Marlborough Region", -37.7846, 175.2797, 13),
    "nelsonregion": ("Nelson Region", -37.7846, 175.2797, 13),
    "northland": ("Northland Region", -37.7846, 175.2797, 13),
    "otago": ("Otago Region", -37.7846, 175.2797, 13),
    "southland": ("Southland Region", -37.7846, 175.2797, 13),
    "taranaki": ("Taranaki Region", -37.7846, 175.2797, 13),
    "tasmanregion": ("Tasman Region", -37.7846, 175.2797, 13),
    "waikatoregion": ("Waikato Region", -37.7846, 175.2797, 13),
    "wellingtonregion": ("Wellington Region", -37.7846, 175.2797, 13),
    "westcoast": ("West Coast Region", -37.7846, 175.2797, 13),
}

# Territorial authorities
TLA = {
    "outsideta": ("Area Outside Territorial Authority", 0, 0, 0),
    "ashburton": ("Ashburton District", -37.7846, 175.2797, 13),
    "auckland": ("Auckland", -37.7846, 175.2797, 13),
    "buller": ("Buller District", -37.7846, 175.2797, 13),
    "carterton": ("Carterton District", -37.7846, 175.2797, 13),
    "centralhawkesbay": ("Central Hawke's Bay District",
                         -37.7846, 175.2797, 13),
    "chathamislands": ("Chatham Islands Territory", -37.7846, 175.2797, 13),
    "centralotago": ("Central Otago District", -37.7846, 175.2797, 13),
    "cristchurch": ("Christchurch City", -37.7846, 175.2797, 13),
    "clutha": ("Clutha District", -37.7846, 175.2797, 13),
    "dunedin": ("Dunedin City", -37.7846, 175.2797, 13),
    "farnorth": ("Far North District", -37.7846, 175.2797, 13),
    "gisborne": ("Gisborne", -37.7846, 175.2797, 13),
    "gore": ("Gore District", -37.7846, 175.2797, 13),
    "grey": ("Grey District", -37.7846, 175.2797, 13),
    "hamilton": ("Hamilton City", -37.7846, 175.2797, 13),
    "hastings": ("Hastings District", -37.7846, 175.2797, 13),
    "hauraki": ("Hauraki District", -37.7846, 175.2797, 13),
    "horowhenua": ("Horowhenua District", -37.7846, 175.2797, 13),
    "hurunui": ("Hurunui District", -37.7846, 175.2797, 13),
    "invercargill": ("Invercargill City", -37.7846, 175.2797, 13),
    "kairoura": ("Kaikoura District", -37.7846, 175.2797, 13),
    "kaipara": ("Kaipara District", -37.7846, 175.2797, 13),
    "kapiticoast": ("Kapiti Coast District", -37.7846, 175.2797, 13),
    "kawerau": ("Kawerau District", -37.7846, 175.2797, 13),
    "lowerhutt": ("Lower Hutt City", -37.7846, 175.2797, 13),
    "mackenzie": ("Mackenzie District", -37.7846, 175.2797, 13),
    "manawatu": ("Manawatu District", -37.7846, 175.2797, 13),
    "marlboroughdistrict": ("Marlborough District", -37.7846, 175.2797, 13),
    "masterton": ("Masterton District", -37.7846, 175.2797, 13),
    "matamatapiako": ("Matamata-Piako District", -37.7846, 175.2797, 13),
    "nelson": ("Nelson", -37.7846, 175.2797, 13),
    "newplymouth": ("New Plymouth District", -37.7846, 175.2797, 13),
    "opotiki": ("Opotiki District", -37.7846, 175.2797, 13),
    "otorohanga": ("Otorohanga District", -37.7846, 175.2797, 13),
    "pororua": ("Porirua City", -37.7846, 175.2797, 13),
    "queenstownlakes": ("Queenstown-Lakes District", -37.7846, 175.2797, 13),
    "rangatikei": ("Rangitikei District", -37.7846, 175.2797, 13),
    "rotorua": ("Rotorua District", -37.7846, 175.2797, 13),
    "ruapehu": ("Ruapehu District", -37.7846, 175.2797, 13),
    "selwyn": ("Selwyn District", -37.7846, 175.2797, 13),
    "southland": ("Southland District", -37.7846, 175.2797, 13),
    "southtaranaki": ("South Taranaki District", -37.7846, 175.2797, 13),
    "southwaikato": ("South Waikato District", -37.7846, 175.2797, 13),
    "southwairarapa": ("South Wairarapa District", -37.7846, 175.2797, 13),
    "stratford": ("Stratford District", -37.7846, 175.2797, 13),
    "tararua": ("Tararua District", -37.7846, 175.2797, 13),
    "tasmandistrict": ("Tasman District", -37.7846, 175.2797, 13),
    "taupo": ("Taupo District", -38.78232, 175.90567, 8),
    "tauranga": ("Tauranga City", -37.68054, 176.15494, 11),
    "tcdc": ("Thames-Coromandel District", -37.7846, 175.2797, 13),
    "timaru": ("Timaru District", -37.7846, 175.2797, 13),
    "upperhutt": ("Upper Hutt City", -37.7846, 175.2797, 13),
    "waikatodistrict": ("Waikato District", -37.7846, 175.2797, 13),
    "waimakariri": ("Waimakariri District", -37.7846, 175.2797, 13),
    "waimate": ("Waimate District", -37.7846, 175.2797, 13),
    "waipa": ("Waipa District", -37.7846, 175.2797, 13),
    "wairoa": ("Wairoa District", -37.7846, 175.2797, 13),
    "waitaki": ("Waitaki District", -37.7846, 175.2797, 13),
    "waitomo": ("Waitomo District", -37.7846, 175.2797, 13),
    "wanganui": ("Wanganui District", -37.7846, 175.2797, 13),
    "wellingtoncity": ("Wellington City", -37.7846, 175.2797, 13),
    "westernbay": ("Western Bay of Plenty District", -37.7846, 175.2797, 13),
    "westland": ("Westland District", -37.7846, 175.2797, 13),
    "whakatane": ("Whakatane District", -37.7846, 175.2797, 13),
    "whangarei": ("Whangarei District", -37.7846, 175.2797, 13),
}


def get_choices(candidate, sort=False):
    """Produce a list of tuples suitable for form widgets.

    When passed an iterable (usually from this settings module), return
    a list of tuples suitable for using in form widgets.
    """

    choices = [('', '---')]
    for item in candidate:
        choices.append((item, item))
    if sort:
        return sorted(choices)

    return choices


def get_site_subtype(site_type=None):
    """Produce a tuple suitable for form widgets.

    This is s special case of the function get_choices. Return a
    sorted list of unique legal values for site_subtype, by iterating
    through the SITE_TYPE structure.
    """

    SUBTYPE = [('', 'None')]

    if site_type:
        for item in SITE_TYPE[site_type]:
            SUBTYPE.append(item, item)

        return sorted(list(set(SUBTYPE)))

    for type in sorted(SITE_TYPE):
        for subitem in sorted(SITE_TYPE[type]):
            SUBTYPE.append((subitem, subitem))

    return sorted(list(set(SUBTYPE)))


def link_dictionary(dic):
    """Produce link, text tuples from settings dictionaries.

    Specifically, this function converts REGION and TLA dictionaries
    into a sorted list of (link, text) tuples.
    """

    linklist = []

    for item in sorted(dic.keys()):
        linklist.append((item, dic[item]))

    return linklist
