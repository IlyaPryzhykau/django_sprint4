from django.contrib import admin

from .models import Category, Location, Post, Comment


class BlogAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at'
    )

    list_editable = (
        'category',
        'is_published'
    )

    search_fields = ('title',)
    list_filter = ('category', 'location')


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'title',
    )


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'text',
        'post',
        'created_at'
    )

    list_editable = (
        'text',

    )

    search_fields = ('author',)
    list_filter = ('author',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Post, BlogAdmin)
