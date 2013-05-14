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
            'browser_name': 'Top navigateurs',
            'browser_name_version': 'Top version de navigateur',
            'size': "Top tailles d'écran",
            'platform': 'Top plateforme',
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
        'browser_name': 'Top browsers',
        'browser_name_version': 'Top browser versions',
        'size': 'Top screen sizes',
        'platform': 'Top platforms',
        'country': 'Top countries',
        'day': 'Top days',
        'ip': 'Top IP addresses'
    }[string]

