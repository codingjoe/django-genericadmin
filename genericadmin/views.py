try: 
    import json
except ImportError: 
    import simplejson as json
    
from django.http import HttpResponse, HttpResponseNotAllowed, Http404
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.widgets import url_params_from_lookup_dict
from django.utils.text import capfirst
from django.core.exceptions import ObjectDoesNotExist
try:
    from django.utils.encoding import force_text 
except ImportError:
    from django.utils.encoding import force_unicode as force_text

def get_obj(content_type_id, object_id):
    obj_dict = {
        'content_type_id': content_type_id,
        'object_id': object_id,
    }
    
    content_type = ContentType.objects.get(pk=content_type_id)
    obj_dict["content_type_text"] = capfirst(force_text(content_type))
    
    try:
        obj = content_type.get_object_for_this_type(pk=object_id)
        obj_dict["object_text"] = capfirst(force_text(obj))
    except ObjectDoesNotExist:
        raise Http404

    return obj_dict

def generic_lookup(request):
    if request.method == 'GET':
        if 'content_type' in request.GET and 'object_id' in request.GET:
            resp = json.dumps(get_obj(request.GET['content_type'], request.GET['object_id']), ensure_ascii=False)
        else:
            resp = ''
        
        return HttpResponse(resp, mimetype='application/json')
    return HttpResponseNotAllowed(['GET'])

def genericadmin_js_init(request, blacklist=(), whitelist=(), url_params={}, generic_fields=[]):
    if request.method == 'GET':
        obj_dict = {}
        for c in ContentType.objects.all():
            val = force_text('%s/%s' % (c.app_label, c.model))
            params = url_params.get('%s.%s' % (c.app_label, c.model), {})
            params = url_params_from_lookup_dict(params)
            if whitelist:
                if val in whitelist:
                    obj_dict[c.id] = (val, params)
            else:
                if val not in blacklist:
                    obj_dict[c.id] = (val, params)
        
        data = {
            'url_array': obj_dict,
            'fields': generic_fields,
        }
        response = HttpResponse(mimetype='application/json')
        json.dump(data, response, ensure_ascii=False)
        return response
    return HttpResponseNotAllowed(['GET'])
