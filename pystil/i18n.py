# -*- coding: utf-8 -*-
# Copyright (C) 2011-2013 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.


def labelize(string, lang):
    """return the label for a criteria"""
    if lang == 'fr':
        return {
            'new': 'Nouvelles visites',
            'unique': 'Visites',
            'all': 'Pages vues',
            'spent_time': u'Temps passé sur de site',
            'hour': 'Visites par heure'
        }[string]

    return {
        'new': 'New visits',
        'unique': 'Visits',
        'all': 'Page hits',
        'spent_time': 'Time spent on site',
        'hour': 'Visits per hour'
    }[string]


def titlize(string, lang):
    """return the label for a criteria"""
    if lang == 'fr':
        return {
            'all': 'Statistiques par jour',
            'asn': "Top fournisseur d'accès",
            'country_code': "Carte du monde des visites",
            'host': 'Top sites',
            'page': 'Pages les plus vues',
            'hash': 'Hashs les plus vus',
            'referrer_domain': 'Top référeurs',
            'hour': 'Visites par heure',
            'subdomain': 'Top sous domaines',
            'browser_name': 'Top navigateurs',
            'browser_name_version': 'Top version de navigateur',
            'size': "Top tailles d'écran",
            'platform': 'Top plateforme',
            'spent_time': 'Temps passé sur le site',
            'country': 'Top pays',
            'day': 'Top jours',
            'ip': 'Top adresses IP',
        }[string]

    return {
        'all': 'Stats by day',
        'asn': 'Top access networks',
        'country_code': 'Visit worldmap',
        'host': 'Top sites',
        'page': 'Most viewed pages',
        'hash': 'Most viewed hashes',
        'referrer_domain': 'Best referrers',
        'hour': 'Visits per hour',
        'subdomain': 'Top subdomains',
        'browser_name': 'Top browsers',
        'browser_name_version': 'Top browser versions',
        'size': 'Top screen sizes',
        'platform': 'Top platforms',
        'spent_time': 'Time spent on site',
        'country': 'Top countries',
        'day': 'Top days',
        'ip': 'Top IP addresses'
    }[string]


def criteria(criterion, lang='us'):
    return {
        'id': 'Identifier',
        'uuid': 'Unique identifier (uuid)',
        'browser_name': 'Browser Name',
        'hash': 'History tag',
        'host': 'Host',
        'browser_version': 'Browser Version',
        'client_tz_offset': 'Timezone',
        'date': 'Date',
        'last_visit': 'Last Visit',
        'ip': 'Ip',
        'language': 'Language',
        'page': 'Page visited',
        'platform': 'Operating system',
        'query': 'Arguments',
        'referrer': 'Referrer',
        'pretty_referrer': 'Pretty Referrer',
        'referrer_domain': 'Referrer domain',
        'site': 'Site url',
        'size': 'Screen Size',
        'time': 'Time spent on site',
        'country': 'Country',
        'country_code': 'Country Code',
        'city': 'City',
        'lat': 'Latitude',
        'lng': 'Longitude',
        'asn': 'Access Service Network',
        'browser_name_version': 'Browser (Name and Version)',
        'day': 'Day Number',
        'hour': 'Hour of day',
        'spent_time': 'Time Spent',
        'subdomain': 'Subdomain',
        'domain': 'Domain'
    }.get(criterion, criterion)
