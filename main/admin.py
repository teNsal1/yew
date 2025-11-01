from django.contrib import admin
from .models import News, NewsImage, Application, Document, CompanyRequisites

class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    inlines = [NewsImageInline]
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('created_at',)

@admin.register(NewsImage)
class NewsImageAdmin(admin.ModelAdmin):
    list_display = ('news', 'image', 'uploaded_at')
    list_filter = ('news',)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'get_service_display', 'created_at', 'status')
    list_filter = ('service', 'created_at', 'status')
    list_editable = ('status',)
    search_fields = ('name', 'email', 'phone')
    date_hierarchy = 'created_at'

    def mark_as_processed(self, request, queryset):
        queryset.update(is_processed=True)
    mark_as_processed.short_description = "Пометить как обработанные"

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')

@admin.register(CompanyRequisites)
class CompanyRequisitesAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'inn', 'ogrn')
    search_fields = ('short_name', 'inn', 'ogrn')

