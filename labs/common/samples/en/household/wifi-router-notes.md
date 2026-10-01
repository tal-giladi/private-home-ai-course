# Wifi router — admin notes

Kept by the person who set the router up. Fictional, for the course.

Model: Kestrel K8 mesh, one main unit and one satellite. Bought 2024-08.

## Addresses

- Main unit: 192.168.1.1
- Satellite: 192.168.1.2
- The home AI machine: 192.168.1.50 (fixed in the router's DHCP settings)
- Printer: 192.168.1.60

## Credentials

- Admin panel: user `admin`, password `kestrel-router-2019`
- Guest network SSID: `Guest-2G`, password `welcome-in-the-summer`
- Home SSID: `Brighton-5G`, password `purple-otter-42`

The guest network is isolated. IoT devices go on it, never on the home network. The smart bulbs, the
doorbell camera and the two smart plugs are all on `Guest-2G`.

## Things that have gone wrong

- The admin password above is the factory default, not one I changed. I keep meaning to.
- Firmware updates: the router checks on boot. It has not updated itself since 2025-01 because the
  satellite loses the link overnight and the check happens before the link is up.
- Port forwarding: none is configured, and none should ever be. The Home Assistant box and the AI
  machine are reached over the VPN, not through this router.
- UPnP is still on. It should be off.

## Wi-Fi problems

- Satellite in the hallway drops the back room every evening around 19:00. Suspect the power
  adapter, not the radio.
- The 2.4 GHz band is crowded. The IoT devices are pinned to 2.4 GHz on purpose because the cheap
  ones do not do 5 GHz.
- Channel width on 5 GHz is 80 MHz. 40 MHz would be more stable at the edge of the house.
