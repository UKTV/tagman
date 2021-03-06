from django.test import TestCase
from django.db import IntegrityError

from tagman.models import Tag, TagGroup
from tagman.tests.models import TestItem, TCI, IgnoreTestItem


class TestTags(TestCase):

    def setUp(self):
        self.group = TagGroup(name="test-group")
        self.group.save()
        self.groupb = TagGroup(name="test-group-b")
        self.groupb.save()
        self.groupc = TagGroup(name="system-group", system=True)
        self.groupc.save()
        self.tag1 = Tag(group=self.group, name="test-tag1")
        self.tag1.save()
        self.tag2 = Tag(group=self.group, name="test-tag2")
        self.tag2.save()
        self.item = TestItem(name="test-item")
        self.item.save()
        self.tags = [self.tag1, self.tag2]

    def test_create_tag(self):
        self.assertIsNotNone(self.tag1.pk)

    def test_create_group(self):
        self.assertIsNotNone(self.group.pk)

    def test_group_name(self):
        """
        Test that the group name is correctly saved on tag

        This is inserted at time of re-factoring code to de-normalise
        group name into Tag.group_name
        """
        self.assertEquals(self.tag1.group_name, self.group.name)

    def test_group_name_change(self):
        """
        Test that group name re-set on group change for tag

        Confirms that de-normalisation works when group changes
        """
        self.assertEquals(self.tag1.group_name, self.group.name)
        self.tag1.group = self.groupb
        self.tag1.save()
        self.assertEquals(self.tag1.group_name, self.groupb.name)

    def test_group_slug(self):
        """
        Test that the group slug is correctly saved on tag

        This is inserted at time of re-factoring code to de-normalise
        group slug into Tag.group_slug
        """
        self.assertEquals(self.tag1.group_slug, self.group.slug)

    def test_group_slug_change(self):
        """
        Test that group slug re-set on group change for tag

        Confirms that de-normalisation works when group changes
        """
        self.assertEquals(self.tag1.group_slug, self.group.slug)
        self.tag1.group = self.groupb
        self.tag1.save()
        self.assertEquals(self.tag1.group_slug, self.groupb.slug)

    def test_unicode(self):
        """
        Does the tag represent itself correctly when stringified
        """
        self.assertEquals(str(self.tag1), "test-group:test-tag1")

    def test_unicode_system_tag(self):
        tag = Tag(group=self.groupc, name="foo")
        tag.save()
        self.assertEquals(str(tag), "*system-group:foo")

    def test_repr_system_tag(self):
        tag = Tag(group=self.groupc, name="foo")
        tag.save()
        self.assertEquals(repr(tag), "system-group:foo")

    def test_repr(self):
        """
        Does the tag represent itself correctly
        """
        self.assertEquals(repr(self.tag1), "test-group:test-tag1")

    def test_denormalised_system_flag(self):
        """
        Does tag reflect its group's system flag
        """
        tag = Tag(group=self.groupc, name="foo")
        tag.save()
        self.assertFalse(self.tag1.group_is_system)
        self.assertFalse(self.tag1.system)
        self.assertTrue(tag.group_is_system)
        self.assertTrue(tag.system)

    def test_group_change_updates_denormalised_tags_name(self):
        """
        Change group name and check tags de-normalised fields update
        """
        self.assertEquals(str(self.tag1), "test-group:test-tag1")
        self.group.name = "new-test-group"
        self.group.save()
        tag = Tag.objects.get(name="test-tag1")
        self.assertEquals(str(tag), "new-test-group:test-tag1")

    def test_group_change_updates_denormalised_tags_slug(self):
        """
        Change group slug and check tags de-normalised fields update
        """
        self.assertEquals(self.tag1.group_slug, "test-group")
        self.group.slug = "new-test-group"
        self.group.save()
        tag = Tag.objects.get(name="test-tag1")
        self.assertEquals(tag.group_slug, "new-test-group")

    def test_group_change_updates_denormalised_tags_system(self):
        """
        Change group system and check tags de-normalised fields update
        """
        self.assertEquals(self.tag1.group_is_system, False)
        self.group.system = True
        self.group.save()
        tag = Tag.objects.get(name="test-tag1")
        self.assertEquals(tag.group_is_system, True)

    def test_add_tag_to_item(self):
        [self.item.tags.add(tag) for tag in self.tags]
        self.assertTrue([tag for tag in self.item.tags.all()
                        if tag in self.tags])

    def test_tags_in_group(self):
        [self.group.tag_set.add(tag) for tag in self.tags]
        self.assertTrue([tag for tag in self.group.tags_for_group()
                         if tag in self.tags])

    def test_unique_tag_in_group(self):
        tag1_clone = Tag(group=self.group, name=self.tag1.name)
        self.assertRaises(IntegrityError, tag1_clone.save)

        # ... also test to see if we can make a tag with the same name as
        # tag1 but a different group. This must now be allowed.
        tag1_noclone = Tag(group=self.groupb, name=self.tag1.name)
        try:
            tag1_noclone.save()
        except IntegrityError, ie:
            self.fail("Unique constraint on group,name fails: {0}"
                      .format(str(ie)))

    def test_unique_tag_in_system_group(self):
        tag = Tag(group=self.groupc, name="foo")
        tag.save()
        tagb = Tag(group=self.groupc, name="foo")
        self.assertRaises(IntegrityError, tagb.save)

    def test_get_tagged_model_items(self):
        self.item.tags.add(self.tag1)
        model_items =\
            self.tag1.tagged_model_items(model_cls=self.item.__class__)
        self.assertTrue(self.item in list(model_items.all()))

    def test_get_tag_for_string(self):
        self.group.tag_set.add(self.tag1)
        self.assertTrue(self.tag1 == Tag.tag_for_string(str(self.tag1)))

    def test_get_tags_for_string(self):
        string = ""
        for idx, tag in enumerate(self.tags):
            self.group.tag_set.add(tag)
            string += "%s%s" % (str(tag), ","
                      if idx + 1 is not len(self.tags) else "")
        self.assertTrue([tag for tag in Tag.tags_for_string(string)
                         if tag in self.tags])

    def test_get_all_tag_groups(self):
        [self.item.tags.add(tag) for tag in self.tags]
        [self.group.tag_set.add(tag) for tag in self.tags]
        self.assertTrue([group for group in self.item.all_tag_groups()
                         if group == self.group])

    def test_add_tag_str(self):
        [self.item.add_tag_str("%s:%s" % (self.group.name, tag.name))
         for tag in self.tags]
        self.assertTrue([tag for tag in self.item.tags.all()
                         if tag in self.tags])

    def test_get_tagged_items(self):
        self.item.tags.add(self.tag1)
        item_model_name = self.item.__class__.__name__.lower()
        # Create a model that should be ignored
        ignored_model = IgnoreTestItem(name="ignore_me")
        ignored_model.save()
        ignored_model.tags.add(self.tag1)
        ignored_model_name = ignored_model.__class__.__name__.lower()
        # first check the default call returns both
        items = self.tag1.tagged_items()
        self.assertTrue(self.item in list(items[item_model_name].all()))
        self.assertTrue(ignored_model in list(items[ignored_model_name].all()))
        # now ignore the model and check that its not returned
        items = self.tag1.tagged_items(ignore_models=[IgnoreTestItem])
        self.assertTrue(self.item in list(items[item_model_name].all()))
        items = self.tag1.tagged_items(ignore_models=[IgnoreTestItem])
        self.assertTrue(self.item in list(items[item_model_name].all()))
        self.assertTrue(ignored_model_name not in items.keys())

    def test_get_tagged_items_filter(self):
        self.item.tags.add(self.tag1)
        item_model_name = self.item.__class__.__name__.lower()
        # Create a model that should be ignored
        ignored_model = IgnoreTestItem(name="ignore_me")
        ignored_model.save()
        ignored_model.tags.add(self.tag1)
        ignored_model_name = ignored_model.__class__.__name__.lower()

        # first check the default call returns both
        items = self.tag1.tagged_items()
        self.assertTrue(self.item in list(items[item_model_name].all()))
        self.assertTrue(ignored_model in list(items[ignored_model_name].all()))

        # now retrieve only the selected models
        items = self.tag1.tagged_items(models=[TestItem])
        self.assertTrue(self.item in list(items[item_model_name].all()))
        self.assertFalse(ignored_model_name in items.keys())
        items = self.tag1.tagged_items(models=[IgnoreTestItem])
        self.assertFalse(item_model_name in items.keys())
        self.assertTrue(ignored_model in list(items[ignored_model_name].all()))
        items = self.tag1.tagged_items(models=[IgnoreTestItem, TestItem])
        self.assertTrue(self.item in list(items[item_model_name].all()))
        self.assertTrue(ignored_model in list(items[ignored_model_name].all()))

    def test_get_unique_item_set(self):
        self.item.tags.add(self.tag1)
        item2 = TestItem(name="test-item-2")
        item2.save()
        item2.tags.add(self.tag1)
        items = self.tag1.unique_item_set()
        self.assertTrue(self.item in items)
        self.assertTrue(item2 in items)

    def test_get_unique_item_set_filtering_models(self):
        self.item.tags.add(self.tag1)
        item2 = TestItem(name="test-item-2")
        item2.save()
        item2.tags.add(self.tag1)
        items = self.tag1.unique_item_set()
        self.assertTrue(self.item in items)
        self.assertTrue(item2 in items)

    def _setup_items_with_tags(self):
        self.item.tags.add(self.tag1)

        ignored_model = IgnoreTestItem(name="ignore_me")
        ignored_model.save()
        ignored_model.tags.add(self.tag1)

        item2 = TestItem(name="test-item-2")
        item2.save()
        item2.tags.add(self.tag1)

    def test_tag_weight(self):
        self._setup_items_with_tags()
        all_tags = Tag.public_objects.get_tags_with_weight()
        expected_all_tags = {'test-group:test-tag1': 3, 'test-group:test-tag2': 0}
        self.assertEquals(all_tags, expected_all_tags)

    def test_tag_weight_with_ignored_model(self):
        self._setup_items_with_tags()
        ignored_model_tags = Tag.public_objects.get_tags_with_weight(
            ignore_models=[IgnoreTestItem]
        )
        expected_ignored_model_tags = {
            'test-group:test-tag1': 2,
            'test-group:test-tag2': 0
        }
        self.assertEquals(ignored_model_tags, expected_ignored_model_tags)

    def test_tag_composite_name(self):
        self._setup_items_with_tags()
        non_composite_name_tags = Tag.public_objects.get_tags_with_weight(composite_name=False)
        expected_non_composite_name_tags = {u'test-tag1': 3, u'test-tag2': 0}
        self.assertEquals(non_composite_name_tags, expected_non_composite_name_tags)


class TestSystemTags(TestCase):
    """
    System tags are designed not to appear in most UI - they are auto-added
    by models so that they can be searched on and have other functionality.
    A custom manager on the Tag prevents these appearing in e.g. admin for
    users when tagging items. But other managers allow access to the whole
    world of tags. Here we test these managers, as well as the rendering of
    system tags.
    """
    def setUp(self):
        self.sys_group = TagGroup(name="system_group", system=True)
        self.sys_group.save()
        self.nonsys_group = TagGroup(name="normal_group", system=False)
        self.nonsys_group.save()

        self.tag_a = Tag(group=self.sys_group, name="tag_a")
        self.tag_b = Tag(group=self.sys_group, name="tag_b")
        self.tag_c = Tag(group=self.nonsys_group, name="tag_c")
        self.tag_d = Tag(group=self.nonsys_group, name="tag_d")
        [getattr(self, "tag_%s" % x).save() for x in "abcd"]

        self.systags = set([self.tag_a, self.tag_b])
        self.nonsystags = set([self.tag_c, self.tag_d])

    def test_manager_public(self):
        nonsystags = set(Tag.public_objects.all())
        self.assertEquals(nonsystags, self.nonsystags)

    def test_manager_systags(self):
        systags = set(Tag.sys_objects.all())
        self.assertEquals(systags, self.systags)

    def test_manager_default(self):
        alltags = set(self.systags)
        alltags.update(self.nonsystags)
        returnedtags = set(Tag.objects.all())
        self.assertEquals(alltags, returnedtags)

    def test_sysgroup_representations(self):
        self.assertEquals(str(self.tag_a), "*system_group:tag_a")

    def test_non_sysgroup_representation(self):
        self.assertEquals(str(self.tag_c), "normal_group:tag_c")

    def test_tag_for_string_system_group(self):
        t = Tag.tag_for_string("*system_group:tag_a")
        self.assertEquals(t, self.tag_a)


class TestSlugification(TestCase):
    def setUp(self):
        self.group = TagGroup(name="normal group", system=False)
        self.group.save()

        self.tag_a = Tag(group=self.group, name="tag a")
        self.tag_b = Tag(group=self.group, name="TAG b")
        self.tag_a.save()
        self.tag_b.save()

    def test_slug_values_a(self):
        self.assertEquals(self.tag_a.slug, "tag-a")

    def test_slug_values_b(self):
        self.assertEquals(self.tag_b.slug, "tag-b")


class TestTaggedContentItem(TestCase):
    """
    Test the features of TaggedContentItem, anything that is tagged
    in some way and which will automatically assign itself tags.
    """
    def setUp(self):
        self.tci = TCI()
        self.tci.save()
        self.tci.associate_auto_tags()
        self.tci.save()

    def test_gen_tag_string(self):
        tag_str = self.tci.self_tag_string
        self.assertEquals(tag_str, '*TCI:tci-slug')

    def test_make_self_tag_name(self):
        name = self.tci._make_self_tag_name()
        self.assertEquals(name, 'tci-slug')

    def test_self_autotag(self):
        """Test method which returns object's own unique auto tag"""
        auto_tag = self.tci.self_auto_tag
        self.assertEquals(auto_tag, Tag.objects.get(slug='tci-slug'))

    def test_auto_tag_creation(self):
        self.tci.associate_auto_tags()
        at = self.tci.auto_tags.all()
        self.assertEquals(len(at), 1)
        tag = at[0]
        self.assertEquals(tag.group.name, 'TCI')
        self.assertEquals(tag.name, 'tci-slug')
        self.assertEquals(tag.system, True)

    def test_get_auto_tagged_items(self):
        self.tci.associate_auto_tags()
        auto_tag = self.tci.auto_tags.all()[0]
        tci_models = list(
            auto_tag.auto_tagged_model_items
            (model_cls=self.tci.__class__).all()
        )
        self.assertTrue(self.tci in tci_models)

    def test_get_tci_from_auto_tag(self):
        """
        Test the Tag.auto_tagged_model_items method by looking to retrieve
        our TCI based on its auto-tag.
        """
        auto_tag = Tag.objects.get(slug='tci-slug')
        item_set = set(auto_tag.auto_tagged_model_items(model_cls=TCI).all())
        self.assertEquals(len(item_set), 1)
        self.assertEquals(item_set.pop(), self.tci)

    def test_tci_change_name_updates_tag_not_add(self):
        """
        If the slug for an item changes, it's self tag should be updated -
        a new tag should not be made
        """
        self.tci.associate_auto_tags()
        auto_tags = self.tci.auto_tags.all()
        self.assertEquals(len(auto_tags), 1)
        self.assertEquals(auto_tags[0].name, "tci-slug")

        # now re-name our content item
        self.tci.slug = "new-tci-slug"
        self.tci.save()
        self.tci.associate_auto_tags()
        auto_tags = self.tci.auto_tags.all()
        self.assertEquals(len(auto_tags), 1)
        self.assertEquals(auto_tags[0].name, "new-tci-slug")
        self.assertEquals(auto_tags[0].slug, "new-tci-slug")
