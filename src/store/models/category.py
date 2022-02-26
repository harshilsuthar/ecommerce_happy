from django.db import models
from treebeard.mp_tree import MP_Node



class Category(MP_Node):

    name = models.CharField(max_length=100)
    available = models.BooleanField()
    node_order_by = ['name']
    
    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return 'Category: %s' % self.name

    @staticmethod
    def get_all_category():
        return Category.get_root_nodes()

    def is_children_available(self):
        return any([child.available for child in self.get_children()])


class CategoryFilterSelector(models.Model):
    category = models.OneToOneField(Category, on_delete=models.CASCADE)
    productAttribute = models.ManyToManyField('store.ProductAttribute', blank=True)
    tagName = models.ManyToManyField('store.TagName', blank=True)
    available = models.BooleanField()
    