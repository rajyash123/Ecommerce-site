from django.db import models

# Create your models here.
class BlogPost(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=20)
    head0 = models.CharField(max_length=500)
    head1 = models.CharField(max_length=500)
    head2 = models.CharField(max_length=500)
    pub_date = models.DateField()
    subcategory = models.CharField(max_length=20, default='')
    thumbnail = models.ImageField(default='')

    def __str__(self):
        return self.title
