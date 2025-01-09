**Fantech X9 Thor Linux Driver**

This repository contains the driver for the Fantech X9 Thor gaming mouse on Linux.

**Installation**

1. Clone the repository:

```bash
git clone https://github.com/centaurusgod/fantech_x9_thor_linux_driver_updated.git
```

2. Navigate to the directory:

```bash
cd fantech_x9_thor_linux_driver_updated
```

3. Make the `mouse` script executable:

```bash
chmod +x mouse
```

4. Copy the `mouse` script to `/usr/bin/` with sudo permissions:

```bash
sudo cp mouse /usr/bin/
```

**Usage**

* `mouse`: Sets the DPI to 2000 and turns off the LED color.
* `mouse -c color_name`: Sets the LED color to `color_name`.
* `mouse -d dpi`: Sets the DPI to `dpi`.
* `mouse -c color_name -d dpi`: Sets the LED color to `color_name` and the DPI to `dpi`.
* Example(all small letter): `mouse -c red`
**Supported Colors**

* yellow
* blue
* violet
* green
* red
* cyan
* white

**Supported DPIs**

* 200
* 400
* 600
* 800
* 1000
* 1200
* 1600
* 2000
* 2400
* 3200
* 4000
* 4800

You can remove the downloaded files by deleting the `fantech_x9_thor_linux_driver_updated` directory.

