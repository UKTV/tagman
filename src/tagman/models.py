"""
Tagman seeks to solve the problem where system designers need both categories
and tags but can't quite describe what the differences really are.

A compound construct, the qualified tag, has a name but is assigned to a group.

These models implement this idea.
"""
import logging

from django.db import models
from django.template.defaultfilters import slugify

TAG_SEPARATOR = ":"
logger = logging.getLogger()


class TagGroup(models.Model):
    """
    A Tag Group is a logical grouping for tags; e.g. tag group 'flavour' could
    have tags 'cinnamon', 'beef' etc which would be distinguish from another
    tag also named 'beef' but in the category 'meat'.
    """
    name = models.CharField(verbose_name='Name', max_length=255, unique=True)
    slug = models.SlugField(max_length=255, default="")
    system = models.BooleanField(default=False,
                                 help_text="Set True for system groups that "
                                           "should not appear for general use")

    def __unicode__(self):
        prefix = "*" if self.system else ""
        return prefix + self.name

    def tags_for_group(self):
        """
        Return the set of tags that are associated with this group
        """
        return self.tag_set.all()

    def save(self, *args, **kwargs):
        """ assign slug if empty """
        if not self.slug:
            self.slug = slugify(self.name)
        super(TagGroup, self).save(*args, **kwargs)

        # update de-normalised values in Tags of this group
        tags_for_group = self.tag_set.all()
        for tag in tags_for_group:
            tag.save()


class TagManager(models.Manager):
    def __init__(self, sys=False, archived=True):
        """
        If sys == True, this will return only system tags. If False,
        the default, will return non-system tags only.
        If archived == False, this will return only non-archived Tags.
        """
        super(TagManager, self).__init__()
        self.system_tags = sys
        self.archived = archived

    def get_query_set(self):
        """
        By default return only those objects that are not flagged as
        'system' tags.
        """
        return super(TagManager, self)\
            .get_query_set()\
            .exclude(group__system=not self.system_tags)\
            .filter(archived=self.archived)

    def get_tags_with_weight(self, ignore_models=[], composite_name=True):
        """
        :param ignore_models: Models to ignore in Tag usage results.
        :param composite_name: If True the group name will be prepended
        to tag name for dict keys.

        Returns dictionary of tag name as key and tag weight (usage) as
        value.
        """
        tag_dict = {}
        tags = super(TagManager, self).get_query_set()
        for tag in tags:
            tag_name = tag.__unicode__() if composite_name else tag.name
            tag_dict[tag_name] = tag.tag_weight(ignore_models)
        return tag_dict


class Tag(models.Model):
    """
    A Tag has a name and is associated with a tag group. Thus we might
    have flavour:cinnamon where the tag is 'cinnamon' and the tag group
    is 'flavour'.
    """
    name = models.CharField(verbose_name='Name', max_length=255)
    slug = models.SlugField(max_length=255, default="")
    group = models.ForeignKey(TagGroup, verbose_name='Group')
    group_name = models.CharField(verbose_name='Group name',
                                  max_length=255, editable=False,
                                  blank=True,
                                  help_text="De-normalised group name")
    group_slug = models.SlugField(max_length=255, default="",
                                  editable=False, blank=True,
                                  help_text="De-normalised group slug")
    group_is_system = models.BooleanField(
        default=False,
        editable=False,
        help_text="De-normalised group system")
    archived = models.BooleanField(default=False)

    objects = models.Manager()
    sys_objects = TagManager(sys=True, archived=False)
    public_objects = TagManager(sys=False, archived=False)
    non_archived = TagManager(sys=False, archived=False)

    def save(self, *args, **kwargs):
        """
        Assign slug if empty
        """
        if not self.slug:
            self.slug = slugify(self.name)

        # de-normalise
        self.group_name = str(self.group) if self.group else ""
        self.group_slug = str(self.group.slug) if self.group else ""
        self.group_is_system = self.group.system

        super(Tag, self).save(*args, **kwargs)

    class Meta:
        unique_together = ("name", "group",)

    def __unicode__(self):
        return u"{0}{1}".format(
            self.group_name + TAG_SEPARATOR if self.group_name else "", self.name
        )

    def __repr__(self):
        return u"{0}{1}".format(
            self.group_slug + TAG_SEPARATOR if self.group_slug else "", self.slug
        )

    def archive(self):
        """
        Set the archive flag to implement soft-delete
        """
        self.archived = True
        self.save()

    @property
    def system(self):
        return self.group_is_system

    def models_for_tag(self):
        """
        Return the unique set of model names, all of which have had
        instances tagged with this tag.
        @todo: This is *really* hacky. Can we do it more elegantly?
        """
        models = set()
        for attribute in dir(self):
            if attribute[-4:] == '_set':
                # we just want the model name, not the set name
                model_name = attribute.split('_')[0]
                models.add(model_name)
        # return the unique set of model names
        return models

    def tagged_model_items(self, model_cls=None, model_name="",
                           only_auto=False):
        """
        Return a query_set of a given model, the class for
        which is passed into model_cls OR the name for which is passed in
        model_name, that are tagged with this tag.

        If `only_auto`==True then return only auto-tagged sets.
        """
        def _get_model_query_set(set_name):
            query_set = None
            try:
                _set = getattr(self, set_name)
            except AttributeError:
                logger.debug("Set {0} not found on tag {1}".format(
                    set_name,
                    self
                ))
            else:
                query_set = _set
            return query_set

        if model_cls:
            cls_name = model_cls.__name__.lower()
        else:
            cls_name = model_name.lower()

        if not only_auto:
            model_set = _get_model_query_set(
                "{0}_set".format(cls_name)
            )
        else:
            model_set = _get_model_query_set(
                "{0}_auto_tagged_set".format(cls_name)
            )

        return model_set

    def auto_tagged_model_items(self, model_cls=None, model_name="",
                                limit=None):
        """
        Convenience method to return all auto-tagged instances for class
        and tag. See tagged_model_items which this calls with
        only_auto=True
        """
        return self.tagged_model_items(model_cls, model_name, only_auto=True)

    def tagged_items(self, only_auto=False, models=None, ignore_models=None):
        """
        Return a dictionary, keyed on model name, with each value the
        query_set of items of that model tagged with this tag.

        :param models:
            A list of model classes for which to retrieve items. If absent,
            retrieve any model that has a foreign key to a tag.
        :param ignore_models:
            Model classes not to include in the list of retrieved items.
        """
        if models is None:
            models = self.models_for_tag()
        else:
            models = [model.__name__.lower() for model in models]

        if ignore_models is None:
            ignore_models = set()
        else:
            ignore_models = set([model.__name__.lower()
                                 for model in ignore_models])

        rdict = {}
        for model in models:
            if model not in ignore_models:
                rdict[model] = self.tagged_model_items(model_name=model,
                                                       only_auto=only_auto)
        return rdict

    def tag_weight(self, ignore_models=[]):
        """
        Returns the weight of a tag based on the tags usage.
        """
        weight = 0
        for model_set in self.tagged_items(
            ignore_models=ignore_models
        ).values():
            if model_set:
                weight += model_set.count()
        return weight

    def unique_item_set(self, limit=None, only_auto=False, models=None,
                        ignore_models=None, filter_dict=None):
        """
        Return the unique item set for a tag.

        :param models:
            Return only instances from these models. If absent, retrieve any
            model that has a foreign key to Tag
        :param ignore_models:
            Do not retrieve instances of these models
        """
        item_set = set()
        tagged_items = self.tagged_items(only_auto=only_auto,
                                         models=models,
                                         ignore_models=ignore_models)
        # merge all tagged items into a unique set
        for model_set in tagged_items.values():
            if model_set:
                model_set = model_set.filter(**filter_dict) \
                    if filter_dict else model_set.all()
                item_set.update(
                    # query set evaluated here
                    model_set[:limit]
                )

        return item_set

    @classmethod
    def tag_for_string(cls, s):
        """
        Given a tag representation as "[*]GRP:NAME", return
        the tag instance.

        @todo: handle the [TagGroup|Tag].DoesNotExist exceptions
        """
        s = s.strip('* ')  # representation of system group prefixed *
        groupname, tagname = s.split(TAG_SEPARATOR)
        try:
            grp = TagGroup.objects.get(name=groupname)
            tag = Tag.objects.get(name=tagname, group=grp)
        except TagGroup.DoesNotExist:
            raise Tag.DoesNotExist()
        return tag

    @classmethod
    def get_or_create(cls, group_name, tag_name, system=False):
        """
        Like get_or_create on a manager but driven by distinct strings and
        creates the TagGroup if required.
        """
        group, _ = TagGroup.objects.get_or_create(name=group_name,
                                                  system=system)
        tag, created = Tag.objects.get_or_create(name=tag_name,
                                                 slug=slugify(tag_name),
                                                 group=group)
        if created:
            logger.debug("Created tag via get_or_create "
                         "with repr {0} and ID {1}"
                         .format(repr(tag), tag.id))
        elif tag.archived:
            tag.archived = False
            tag.save()
        return tag

    @classmethod
    def get_or_create_tag_for_string(cls, s):
        """
        Given a tag representation as "[*]GRP:NAME", return the tag
        instance.
        """
        group, name = s.strip('* ').split(':')
        is_system = True if s.strip()[0] == '*' else False
        return Tag.get_or_create(group, name, is_system)

    @classmethod
    def tags_for_string(cls, s):
        """
        Given a comma delimited list of tag string representations, e.g.::

        <GRP>:<NAME>,<GRP>:<NAME2>...

        return the list of tag instances that these represent.
        @todo: handle case where no tag instance returned
        """
        tokens = s.strip().split(',')
        _tags = [Tag.tag_for_string(t) for t in tokens]
        if not _tags:
            return None
        return _tags


class TaggedItem(models.Model):
    """
    Abstract base class for all models that wish to have tagging. Provides
    `tags` and `auto_tags` fields as well as convenience methods
    for setting and querying.
    """
    tags = models.ManyToManyField(Tag, related_name="%(class)s_set",
                                  blank=True)
    auto_tags = models.ManyToManyField(
        Tag,
        related_name="%(class)s_auto_tagged_set",
        blank=True, editable=False)

    class Meta:
        abstract = True

    def add_tag_str(self, string, auto_tag=False):
        """
        Create a tag from a string and add to tags.

        If auto_tag = True, return from the auto_tags list instead of tags
        """
        tags = self.auto_tags if auto_tag else self.tags
        tag = Tag.get_or_create_tag_for_string(string)
        tags.add(tag)
        return tag

    def all_tag_groups(self, auto_tag=False):
        """
        Return all set of unique tag groups of tags associated with this
        instance. If auto_tag = True, return from the auto_tags list instead
        of tags
        """
        tags = self.auto_tags if auto_tag else self.tags
        return set(tag.group for tag in tags.all())


class TaggedContentItem(TaggedItem):
    """
    Mixin for models that would have features such as auto-tagging
    enabled.
    """
    class Meta:
        abstract = True

    def _make_self_tag_name(self):
        """
        Override this in concrete class to change the slug used, for example
        if the slug field is not called `slug`
        """
        return self.slug

    @property
    def self_tag_string(self):
        """
        Generate the string representation for the auto tag that this
        should be assigned. e.g. return `*<classname>:<tag name>`
        """
        tag_group = self.__class__.__name__
        tag_name = self._make_self_tag_name()
        return "*{0}:{1}".format(tag_group, tag_name)

    @property
    def self_auto_tag(self):
        """
        Return the tag instance that is this object's own auto tag
        """
        tag_str = self.self_tag_string
        my_tag = [t for t in self.auto_tags.all() if str(t) == tag_str]
        if not my_tag:
            raise Exception("{0} has yet to be auto-tagged".format(self))
        return my_tag[0]

    def associate_auto_tags(self):
        """
        Automatically tag myself (by adding to auto_tags):
        *<model name>:<slug>.

        Typically this method would be called on an instance in a post-save
        signal handler for a model.

        Checks for an existing tag having the group of self.__class__.__name__
        and, if so, changes the name rather than create a new tag and
        thus ensures existing references remain valid.
        """
        tag_group = "*{}".format(self.__class__.__name__)
        auto_tags = [t for t in self.auto_tags.all()
                     if t.group_name == tag_group]

        # we allow for old data prior to this fix when changing
        # name resulted in more than one self-tag being added. Collapsing these
        # is a dangerous migration so we leave them and amend the last in the
        # list which will be the 'current' one
        if auto_tags:
            tag = auto_tags[-1]
            tag.name = self._make_self_tag_name()
            # Ensure the auto tag is not archived if this is a new item with
            # the same name as an old item
            tag.archived = False
            # we let tag save handler create the slug which it will do so
            # if it finds an empty string.
            tag.slug = ""
            tag.save()
        else:
            tag = self.add_tag_str(self.self_tag_string, auto_tag=True)

        logger.info("Auto tagging {0} with {1}".format(str(self), repr(tag)))

        return tag
