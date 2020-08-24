import random

planets = [
    'Mercury',
    'Venus',
    'Earth',
    'Mars',
    'Jupiter',
    'Saturn',
    'Uranus',
    'Neptune',
    'Pluto'
]

# Only small, single word country names are used for obfuscation
countries = [
    'Afghanistan',
    'Albania',
    # 'American_Samoa',
    'Andorra',
    'Angola',
    'Anguilla',
    # 'Antigua_and_Barbuda',
    'Argentina',
    'Armenia',
    'Aruba',
    'Australia',
    'Austria',
    'Bahamas',
    'Bahrain',
    'Bangladesh',
    'Barbados',
    'Belgium',
    'Belize',
    'Benin',
    'Bermuda',
    'Bhutan',
    'Bolivia',
    # 'Bosnia_and_Herzegovina',
    'Botswana',
    'Brazil',
    'Brunei',
    'Bulgaria',
    # 'Burkina_Faso',
    'Cambodia',
    'Cameroon',
    'Canada',
    # 'Cape_Verde',
    # 'Cayman_Islands',
    'Chile',
    'China',
    'Colombia',
    'Congo',
    # 'Costa_Rica',
    'Croatia',
    'Cyprus',
    # 'Czech_Republic',
    'Denmark',
    'Dominica',
    # 'Dominican_Republic',
    'Ecuador',
    'Egypt',
    # 'El_Salvador',
    # 'Equatorial_Guinea',
    'Eritrea',
    'Ethiopia',
    # 'Faroe_Islands',
    'Fiji',
    'Finland',
    'France',
    # 'French_Guiana',
    # 'French_Polynesia',
    'Georgia',
    'Germany',
    'Ghana',
    'Gibraltar',
    'Greece',
    'Grenada',
    'Guadeloupe',
    'Guam',
    'Guatemala',
    'Guyana',
    'Haiti',
    'Honduras',
    'Hong_Kong',
    'Hungary',
    'Iceland',
    'India',
    'Indonesia',
    'Iran',
    'Iraq',
    'Ireland',
    'Italy',
    'Ivory_Coast',
    'Jamaica',
    'Japan',
    'Jordan',
    'Kazakhstan',
    'Kenya',
    'Kuwait',
    'Kyrgyzstan',
    'Laos',
    'Latvia',
    'Lebanon',
    'Lesotho',
    'Libya',
    'Liechtenstein',
    'Lithuania',
    'Luxembourg',
    'Macao',
    'Malawi',
    'Malaysia',
    'Malta',
    'Marshall_Islands',
    'Martinique',
    'Mauritius',
    'Mayotte',
    'Mexico',
    'Micronesia',
    'Moldova',
    'Monaco',
    'Mongolia',
    'Montserrat',
    'Mozambique',
    'Myanmar',
    'Namibia',
    'Nepal',
    'Netherlands',
    # 'Netherlands_Antilles',
    # 'New_Caledonia',
    # 'New_Zealand',
    'Nicaragua',
    'Niger',
    'Nigeria',
    'Norway',
    'Oman',
    'Pakistan',
    'Palestine',
    'Panama',
    'Paraguay',
    'Peru',
    'Philippines',
    'Poland',
    'Portugal',
    'Puerto_Rico',
    'Qatar',
    'Reunion',
    'Romania',
    'Russia',
    'Rwanda',
    # 'Saint_Kitts_and_Nevis',
    # 'Saint_Lucia',
    # 'Saint_Vincent_and_The_Grenadines',
    # 'Saudi_Arabia',
    'Serbia',
    'Singapore',
    'Slovakia',
    'Slovenia',
    # 'South_Africa',
    # 'South_Korea',
    'Spain',
    # 'Sri_Lanka',
    'Sudan',
    # 'Sudan_South',
    'Suriname',
    'Swaziland',
    'Sweden',
    'Switzerland',
    'Syria',
    'Taiwan',
    'Tajikistan',
    'Tanzania',
    'Thailand',
    # 'Trinidad_and_Tobago',
    'Turkey',
    'Turkmenistan',
    # 'Turks_and_Caicos_Islands',
    'Uganda',
    'Ukraine',
    # 'United_Kingdom',
    # 'United_States',
    # 'United_States_Virgin_Islands',
    'Uruguay',
    'Uzbekistan',
    'Vatican',
    'Venezuela',
    'Vietnam',
    'Wallis_and_Futuna',
    'Yemen',
]


class ObfuscateTransformer:
    """The default is to replace every literal value in the plan with three asterisks."""

    def __init__(self):
        # The types which we are censoring
        self._types = [
            # "bit",
            "bte",
            "sht",
            "int",
            "lng",
            "hge",
            "oid",
            "flt",
            "dbl",
            "str",
            "color",
            "date",
            "daytime",
            "time",
            "timestamp",
            "timezone",
            "blob",
            "inet",
            "url",
            "json"
        ]
        self.schema_mapping = dict()
        self.table_mapping = dict()
        self.column_mapping = dict()

    # obfuscation is MAL instruction specific
    def __call__(self, json_object):
        rdict = dict(json_object)
        vars = rdict.get("args", [])

        # map schema information
        if rdict['module'] == 'sql' and (rdict['function'] == 'bind' or rdict['function'] == 'bind_idx'):
            vars[2]["value"] = self.obfuscate_schema(vars[2]["value"])
            vars[3]["value"] = self.obfuscate_table(vars[3]["value"])
            vars[4]["value"] = self.obfuscate_column(vars[4]["value"])

        # map selections and arithmetics
        elif rdict['module'] == 'algebra' and rdict['function'] == 'thetaselect':
            vars[3]["value"] = self.obfuscate_data(vars[3]["value"], vars[3]["type"])

        elif rdict['module'] == 'algebra' and rdict['function'] == 'select':
            vars[3]["value"] = self.obfuscate_data(vars[3]["value"], vars[3]["type"])
            vars[4]["value"] = self.obfuscate_data(vars[4]["value"], vars[4]["type"])

        else:
            for var in vars:
                # hide the table information
                alias = var.get("alias")
                s, t, c = alias.split('.')
                s = self.obfuscate_schema(s)
                t = self.obfuscate_table(s)
                c = self.obfuscate_column(s)
                var["alias"] = '.'.join([s, t, c])
        return rdict

    def obfuscate_schema(self, original):
        if original in self.schema_mapping:
            return self.schema_mapping[original]
        picked = random.choose(planets)
        self.schema_mapping[original] = picked
        del planets[picked]
        return picked

    def obfuscate_table(self, original):
        if original in self.table_mapping:
            return self.table_mapping[original]
        picked = random.choose(countries)
        self.table_mapping[original] = picked
        del countries[picked]
        return picked

    def obfuscate_column(self, original):
        if original in self.column_mapping:
            return self.column_mapping[original]
        picked = "col_"+str(len(self.column_mapping))
        self.column_mapping[original] = picked
        return picked

    def obfuscate_data(original, tpe):
        # should be refined
        if tpe == ':str':
            picked = '***'
        else:
            picked = original
        return picked
