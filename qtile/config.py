from libqtile import layout, hook
from libqtile.config import Click, Drag, Group, Key, Match, ScratchPad, DropDown
from libqtile.lazy import lazy
from settings.keys import keys
from settings.screens import screens
import os, random, subprocess

mod = "mod4"
terminal = "kitty"

groups=[Group("1",
              layout="columns",
              label="一"),
        Group("2",
              layout="columns",
              label="二"),
        Group("3",
              label="三"),
        Group("4",
              label="四"),
        Group("5",
              label="五")]

for i in groups:
    keys.extend(
        [
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc="Switch to group {}".format(i.name),
            ),
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name),
                desc="Switch to & move focused window to group {}".format(i.name),
            ),
        ]
    )

groups.append(
        ScratchPad("scratchpad", [
            DropDown("term", terminal, opacity=0.8, height=0.6, width=0.7, x=0.15, y=0.2),
        ]),
    )

keys.extend(
        [
        ]
    )
layouts = [
    layout.Columns(border_focus="#7AA2F7",
                   border_normal="#00000000",
                   border_width=5,
                   margin=5,
                   margin_y=3,
                   insert_postion=1),
    layout.Max(),
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    layout.MonadTall(border_focus="#7AA2F7",
                     border_normal="#00000000",
                     border_width=5),

    layout.MonadWide(border_focus="#7AA2F7",
                     border_normal="#00000000",
                     border_width=5),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

widget_defaults = dict(
    font="JetBrainsMono Nerd Font",
    fontsize=16,
)

extension_defaults = widget_defaults.copy()


# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
        Match(title="Screenshot"),  # Screenshot tool
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
# wmname = "LG3D"
wmname = "Qtile"

@hook.subscribe.startup_once
def autostart():
    script = os.path.expanduser("~/.config/qtile/autostart.sh")
    subprocess.Popen([script])
    # lazy.function(set_wallpaper)
    set_wallpaper()
