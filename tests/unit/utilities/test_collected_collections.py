# -*- coding: utf-8 -*-
# (c) 2022 Brian Scholer (@briantist)

import pytest
from unittest import mock

from datetime import datetime, timedelta
from types import GeneratorType
import semver

from galactory.utilities import collected_collections


def test_collected_collections_skip_dirs(repository):
    with mock.patch('artifactory.ArtifactoryFileStat', mock.Mock(return_value=mock.Mock(is_dir=True, children=[]))):
        collections = collected_collections(repository)
        assert collections == {}


@pytest.mark.parametrize('props', [{}, {'version': []}])
def test_collected_collections_skip_missing_version(repository, props):
    with mock.patch.object(repository.__class__, 'properties', property(mock.Mock(return_value=props))):
        collections = collected_collections(repository)
        assert collections == {}


@pytest.mark.parametrize('namespace', [None, 'community', 'briantist', 'fake'])
@pytest.mark.parametrize('collection', [None, 'whatever', 'hashi_vault', 'fake'])
@pytest.mark.parametrize('scheme', [None, '', 'https'])
def test_collected_collections_any(repository, discover_collections, namespace, collection, scheme, app_request_context):
    fqcn = None if any([namespace is None, collection is None]) else f"{namespace}.{collection}"

    collections = collected_collections(repository, namespace, collection, scheme)

    discover_collections.assert_called_once_with(repository, namespace=namespace, name=collection, scheme=scheme)

    contents = list(repository)

    assert isinstance(collections, dict)

    if 'fake' in [namespace, collection]:
        assert collections == {}

    if scheme is None:
        expected_scheme = 'http://'
    elif scheme == '':
        expected_scheme = '//'
    else:
        expected_scheme = scheme

    cols = 0
    for col, data in collections.items():
        assert fqcn is None or col == fqcn
        assert 'latest' in data
        assert 'versions' in data
        assert data['latest']['version'] in data['versions']
        assert data['latest']['download_url'].startswith(expected_scheme), data['latest']['download_url']

        for v, vd in data['versions'].items():
            cols += 1
            ver = next(discover_collections(repository, namespace=vd['namespace']['name'], name=vd['name'], version=v, scheme=scheme))
            assert ver == vd

    assert cols <= len(contents)
