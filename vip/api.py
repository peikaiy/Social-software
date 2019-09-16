from lib.http import render_json
from vip.models import Vip


def show_all_perms(request):
    vip_info = []
    for vip in Vip.objects.all():
        curr_vip = vip.to_dict()
        curr_vip['perms'] = []
        for perm in vip.perms:
            curr_vip['perms'].append(perm.to_dict())
        vip_info.append(curr_vip)
    return render_json(vip_info)
