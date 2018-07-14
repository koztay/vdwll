import Xlib.display

WINDOW_NAME = 'kemal@kemal-MacBookPro: ~'

d = Xlib.display.Display()
r = d.screen().root

Xlib.X.SubstructureRedirectMask = True

x = -1500
y = -1500
# width = r.get_geometry().width
# height = r.get_geometry().height - y

window_ids = r.get_full_property(
    d.intern_atom('_NET_CLIENT_LIST'), Xlib.X.AnyPropertyType
).value

print('window id_ler', window_ids)
desktop_window = None

for window_id in window_ids:
    window = d.create_resource_object('window', window_id)
    print(window.get_wm_name(), window_id)
    if window.get_wm_name() == 'Desktop':
        desktop_window = d.create_resource_object('window', window_id)
        print('Moving Desktop Window')
        desktop_window.configure(
            x=x,
            y=y,
            width=4000,
            height=4000,
            border_width=0,
            stack_mode=Xlib.X.Above
        )
        d.sync()


for window_id in window_ids:
    window = d.create_resource_object('window', window_id)
    print(window.get_wm_name(), window_id)
    if window.get_wm_name() == WINDOW_NAME:
        window.change_attributes(override_redirect=True)
        print('Moving Window')
        window.configure(
            override_redirect=True,
            x=-1500,
            y=-1500,
            # width=width,
            # height=height,
            border_width=0,
            stack_mode=Xlib.X.Above,
        )


        d.sync()


