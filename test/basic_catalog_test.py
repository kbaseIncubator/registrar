

import unittest
import os

from pprint import pprint

from catalog_test_util import CatalogTestUtil
from biokbase.catalog.Impl import Catalog


# tests all the basic get methods
class BasicCatalogTest(unittest.TestCase):


    def test_version(self):
        self.assertEqual(self.catalog.version(self.cUtil.anonymous_ctx()),['0.0.2'])


    def test_is_registered(self):
        self.assertEqual(self.catalog.is_registered(self.cUtil.anonymous_ctx(),
            {'module_name':'onerepotest'}),
            [1])
        self.assertEqual(self.catalog.is_registered(self.cUtil.anonymous_ctx(),
            {'git_url':'https://github.com/kbaseIncubator/onerepotest'}),
            [1])
        self.assertEqual(self.catalog.is_registered(self.cUtil.anonymous_ctx(),
            {'module_name':'onerepotest','git_url':'https://github.com/kbaseIncubator/onerepotest'}),
            [1])
        self.assertEqual(self.catalog.is_registered(self.cUtil.anonymous_ctx(),
            {'module_name':'wrong_name'}),
            [0])
        self.assertEqual(self.catalog.is_registered(self.cUtil.anonymous_ctx(),
            {'module_name':'wrong_name','git_url':'https://github.com/kbaseIncubator/onerepotest'}),
            [0])
        self.assertEqual(self.catalog.is_registered(self.cUtil.anonymous_ctx(),
            {'module_name':'onerepotest','git_url':'wrong_url'}),
            [0])
        self.assertEqual(self.catalog.is_registered(self.cUtil.anonymous_ctx(),
            {'git_url':'wrong_url'}),
            [0])
        self.assertEqual(self.catalog.is_registered(self.cUtil.anonymous_ctx(),
            {}),
            [0])


    def test_list_requested_releases(self):
        requested_releases = self.catalog.list_requested_releases(self.cUtil.anonymous_ctx())[0]
        found_modules = []
        for r in requested_releases:
            self.assertIn('module_name',r)
            found_modules.append(r['module_name'])
            self.assertIn('owners',r)
            self.assertIn('timestamp',r)
            self.assertIn('git_url',r)
            self.assertIn('git_commit_message',r)
            self.assertIn('git_commit_hash',r)
            if r['module_name'] == 'pending_first_release' :
                self.assertEqual(r['git_commit_hash'],    'b843888e962642d665a3b0bd701ee630c01835e6')
                self.assertEqual(r['git_commit_message'], 'update for testing')
                self.assertEqual(r['git_url'],            'https://github.com/kbaseIncubator/pending_Release')
                self.assertEqual(r['timestamp'],          1445023985597)
                self.assertIn('kbasetest',r['owners'])
            if r['module_name'] == 'pending_second_release' :
                self.assertEqual(r['git_url'],            'https://github.com/kbaseIncubator/pending_second_release')
                self.assertIn('rsutormin',r['owners'])
                self.assertIn('wstester1',r['owners'])

        self.assertIn('pending_first_release',found_modules)
        self.assertIn('pending_second_release',found_modules)



    def test_list_basic_module_info(self):

        # default should include all modules that are released
        default = self.catalog.list_basic_module_info(self.cUtil.anonymous_ctx(),
            {})[0]
        module_names = []
        for m in default:
            module_names.append(m['module_name'])
        self.assertEqual(
            ",".join(sorted(module_names)),
            ",".join(['onerepotest','pending_second_release','release_history'])
            )

        # all released and unreleased
        include_unreleased = self.catalog.list_basic_module_info(self.cUtil.anonymous_ctx(),
            {'include_unreleased':1})[0]
        module_names = []
        for m in include_unreleased:
            module_names.append(m['module_name'])
        self.assertEqual(
            ",".join(sorted(module_names)),
            ",".join(sorted(['denied_release','onerepotest','pending_first_release','pending_second_release',
                'registration_error','registration_in_progress','release_history']))
            )

        # no released and no unreleased
        include_nothing = self.catalog.list_basic_module_info(self.cUtil.anonymous_ctx(),
            {'include_released':0})[0]
        module_names = []
        for m in include_nothing:
            module_names.append(m['module_name'])
        self.assertEqual(
            ",".join(sorted(module_names)),
            ",".join([])
            )

        #only unreleased modules
        only_unreleased = self.catalog.list_basic_module_info(self.cUtil.anonymous_ctx(),
            {'include_released':0, 'include_unreleased':1})[0]
        module_names = []
        for m in only_unreleased:
            module_names.append(m['module_name'])
        self.assertEqual(
            ",".join(sorted(module_names)),
            ",".join(sorted(['denied_release','pending_first_release','registration_error',
                'registration_in_progress']))
            )

        inactive = self.catalog.list_basic_module_info(self.cUtil.anonymous_ctx(),
            {'include_disabled':1,'include_released':0,'include_unreleased':1})[0]
        module_names = []
        for m in inactive:
            module_names.append(m['module_name'])
        self.assertEqual(
            ",".join(sorted(module_names)),
            ",".join(sorted(['inactive_module','denied_release','pending_first_release','registration_error',
                'registration_in_progress']))
            )

    def test_get_module_state(self):
        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),
            {'module_name':'onerepotest'})[0]
        pass


    def test_get_module_info(self):
        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),
            {'module_name':'onerepotest'})[0]
        self.assertEqual(info['module_name'],'onerepotest')
        self.assertEqual(info['git_url'],'https://github.com/kbaseIncubator/onerepotest')
        self.assertEqual(info['description'],'KBase module for integration tests of docker-based service/async method calls')
        self.assertEqual(info['owners'],['rsutormin','wstester1'])
        self.assertEqual(info['language'],'python')

        self.assertEqual(info['release']['git_commit_hash'],'49dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(info['release']['timestamp'],1445022818884)
        self.assertEqual(info['release']['git_commit_message'],'added username for testing')
        self.assertEqual(info['release']['version'],'0.0.1')
        self.assertEqual(info['release']['narrative_methods'],['send_data'])

        self.assertEqual(info['beta']['git_commit_hash'],'b843888e962642d665a3b0bd701ee630c01835e6')
        self.assertEqual(info['beta']['timestamp'],1445023985597)
        self.assertEqual(info['beta']['git_commit_message'],'update for testing')
        self.assertEqual(info['beta']['version'],'0.0.1')
        self.assertEqual(info['beta']['narrative_methods'],['send_data'])

        self.assertEqual(info['dev']['git_commit_hash'],'b06c5f9daf603a4d206071787c3f6184000bf128')
        self.assertEqual(info['dev']['timestamp'],1445024094055)
        self.assertEqual(info['dev']['git_commit_message'],'another change')
        self.assertEqual(info['dev']['version'],'0.0.1')
        self.assertEqual(info['dev']['narrative_methods'],['send_data'])


        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),
            {'git_url':'https://github.com/kbaseIncubator/pending_Release'})[0]

        self.assertEqual(info['module_name'],'pending_first_release')
        self.assertEqual(info['git_url'],'https://github.com/kbaseIncubator/pending_Release')
        self.assertEqual(info['description'],' something')
        self.assertEqual(info['owners'],['kbasetest'])
        self.assertEqual(info['language'],'perl')
        self.assertTrue(info['release'] is None)
        

    def test_get_version_info(self):
        pass

    def test_list_released_module_versions(self):
        pass

    

    @classmethod
    def setUpClass(cls):
        cls.cUtil = CatalogTestUtil('.') # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog = Catalog(cls.cUtil.getCatalogConfig())

    @classmethod
    def tearDownClass(cls):
        cls.cUtil.tearDown()





