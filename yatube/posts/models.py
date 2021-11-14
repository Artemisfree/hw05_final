from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.deletion import CASCADE

User = get_user_model()


class Group(models.Model):
    title = models.CharField('group_title', max_length=200)
    slug = models.SlugField('group_slug', unique=True)
    description = models.TextField('group_description')

    class Meta:
        verbose_name_plural = 'groups'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField('post_text')
    pub_date = models.DateTimeField('pub_date', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='post_author',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='group_title',
    )
    image = models.ImageField(
        'picture',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        verbose_name_plural = 'posts'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='comments',
        verbose_name='comment_author',
    )
    text = models.TextField('comment_text')
    created = models.DateTimeField('created', auto_now_add=True)

    class Meta:
        verbose_name_plural = 'comments'
        ordering = ('-created',)

    def __str__(self) -> str:
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='following',
    )

    def clean(self):
        if self.user == self.author:
            raise ValidationError(
                'author and user should be different'
            )

    class Meta:
        models.UniqueConstraint(
            fields=['user', 'author'], name='unique_follow'
        )
