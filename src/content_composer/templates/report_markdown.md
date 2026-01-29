# {{ analysis.title }}

> 视频ID: {{ analysis.video_id }}
>
> 关键技术点: {{ analysis.key_moments|length }} 个

---

## 📹 内容概要

{{ analysis.content }}

---

## 🔑 关键技术详解

{% for moment in analysis.key_moments %}
### {{ loop.index }}. {{ moment.technique }}

**⏱️ 时间点**: `{{ moment.timestamp }}`秒
{% if moment.duration %} **🎬 时长**: `{{ moment.duration }}`秒{% endif %}
{% if moment.media_type == 'gif' %} **🎞️ 类型**: GIF演示{% endif %}

#### 技术说明

{{ moment.description }}

{% if moment.media_asset %}
#### 媒体演示

![{{ moment.technique }}]({{ moment.media_asset.local_path }})
{% endif %}

---

{% endfor %}

## 📊 技术统计

- **技术总数**: {{ analysis.key_moments|length }} 项
- **GIF演示**: {{ analysis.key_moments|selectattr('media_type', 'equalto', 'gif')|list|length }} 个
- **静态图片**: {{ analysis.key_moments|selectattr('media_type', 'equalto', 'static')|list|length }} 个

---

## 🎯 总结

本视频详细讲解了 {{ analysis.key_moments|length }} 项关键技术，通过慢动作演示和详细讲解，帮助你掌握正确的技术要领。

---

*内容由 MotoStep 自动生成*
*来源视频: {{ analysis.video_id }}*
*生成时间: {{ metadata.created_at|default('2026-01-30') }}*
