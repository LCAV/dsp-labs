# STM32CubeIDE

_Note: these instruction and images were produced on October 1, 2019._

The following steps are the same for Windows, Linux, and MacOS as they simply consist of downloading the installation files. For the actual installation, please refer to the corresponding subsection after the following five steps:

## Download instructions

The following steps are the same for Windows, Linux, and MacOS as they simply consist of downloading the installation files. Please refer to the distributor website for detailed installation instructions. Please refer to the corresponding subsection after the following instructions for our additional remarks.

![](../../.gitbook/assets/1_get_software-1.PNG)

2\) Select the download link according to your operating system.

![](../../.gitbook/assets/screenshot-2019-09-25-at-12.14.38-2.png)

4\) You will be asked to log-in in order to pursue with the download, please create an account and follow the instructions.

5\) When you will have completed the log-in, the download will normally start.

6\) Open the installer and follow the steps. You need to perform a standard installation. Some driver will also be installed during the process. Don't skip this.

[Here](eclipse_tips.md), we provide some useful shortcuts tips when working with Eclipse-based tools like SW4STM32.

## Windows

_Note: the instructions were tested using Windows 10 Pro Insider Preview, Version 1607, with a 64-bit operating system on February 11, 2018._

1\) Double-click the EXE file to launch the installation wizard.

![](../../.gitbook/assets/1_initial_win.PNG)

2\) You will have to accept two license agreements to proceed with the installation, after which you will be asked to specify the installation path \(see below\). If the path does not exist, you will be asked to create the directory.

![](../../.gitbook/assets/2_installation_path.PNG)

3\) Next, you can select which packs to install; leave as is. You can then decide to create a Start Menu/Desktop shortcut. You will then be asked to confirm your installation path and packs to install. Pressing "Next" will start the installation \(see below\).

![](../../.gitbook/assets/4_create_shortcuts.PNG)

![](../../.gitbook/assets/5_confirm.PNG)

4\) During the installation, a separate wizard will also pop-up to install necessary ST drivers \(see below\). Proceed with the installation by pressing "Next".

![](../../.gitbook/assets/7_driver_setup.PNG)

5\) When the driver installation has been successfully completed, you should see something similar to the window pane below.

![](../../.gitbook/assets/8_driver_setup_complete.PNG)

6\) You can then proceed to the final pane of the installation by pressing "Next" in the original Installation Wizard \(see below\). Finally, press "Done" to finish the installation!

![](../../.gitbook/assets/9_finish_installation.PNG)

![](../../.gitbook/assets/10_close_installer.PNG)

7\) You can launch the software by using one of the shortcuts created before. You will be prompted to select a workspace \(see below\); we recommend creating a workspace called `"COM303-Workspace"` for the exercises we will be doing.

![](../../.gitbook/assets/11_workspace.PNG)

8\) After setting the workspace, you should see something like the figure below.

![](../../.gitbook/assets/12_sw4stm32.PNG)

You can now proceed to creating [your first project](../instructions.md)!

## Linux

_Note: the following instructions were tested using Ubuntu 16.04.1 LTS, x86\_64 architecture on a Lenovo Thinkpad X230 on February 9, 2018._

1\) From a terminal, navigate to the directory where the downloaded RUN and checksum files are located. Check the permissions with the following command:

```bash
$ ls -l
```

If you do not see an `x` in the permissions for the RUN file:

```bash
>> -rw-rw-r-- ... install_sw4stm32_linux_64bits-vX.X.run
```

You will have to give execution rights to the file as such:

```bash
$ chmod a+x install_sw4stm32_linux_64bits-vX.X.run
```

The `ls -l` command should then show something like:

```bash
>> -rwxrwxr-x install_sw4stm32_linux_64bits-vX.X.run
```

2\) Before running the installation file, please read the warnings for Linux at the bottom of [this page](http://www.openstm32.org/Downloading%2Bthe%2BSystem%2BWorkbench%2Bfor%2BSTM32%2Binstaller#Linux) \(you need to be logged in\). You may have to install a few libraries; we installed `gksudo`, `libc6:i386`, and `lib32ncurses5` and used Java 1.8.0\_151 during our installation.

3\) You can then run the installation file as so:

```bash
$ ./install_sw4stm32_linux_64bits-vX.X.run
```

The checksum file will be used to check the download integrity which may take some time. Eventually, a window pane similar to below should pop up.

![](../../.gitbook/assets/1_initial_linux.png)

4\) You will have to accept two license agreements to proceed with the installation, after which you will be asked to specify the installation path. If the path does not exist, you will be asked to create the directory. Take note of this directory because you will have to navigate here to run the software!

![](../../.gitbook/assets/5_specify_path.png)

5\) Next, you can select which packs to install; leave as is. You will then be asked to confirm your installation path and packs to install. Pressing "Next" will start the installation \(see below\).

![](../../.gitbook/assets/7_select_packs.png)

![](../../.gitbook/assets/8_confirm_packs.png)

6\) When the installation is done, the progress bars will appear as below. Click "Next" to finish the installation procedure and to proceed to the final pane of the installation wizard. Press "Done" and the installation is complete!

![](../../.gitbook/assets/9_installation_done.png)

![](../../.gitbook/assets/11_close_installer.png)

_Note: you may have to enter your computer password for certain "rules" to be added to_ `"/etc/udev/rules.d"` _during the installation \(see below\)._

![](../../.gitbook/assets/10_enter_pwd_rules.png)

7\) You can run the software by navigating from a terminal to the directory where SW4STM32 was installed and running the following command \(or double-clicking from a file explorer\):

```bash
$ ./eclipse
```

The application is called `"eclipse"` since the software is based off of Eclipse.

8\) You will be prompted to select a workspace \(see below\); we recommend creating a workspace called "COM303-Workspace" for the exercises we will be doing.

![](../../.gitbook/assets/12_select_workspace_1.png)

After setting the workspace, you should see a window pane similar to below.

![](../../.gitbook/assets/13_sw4stm32.png)

You can now proceed to creating [your first project](../instructions.md)!

## MacOS

_Note: the instructions were tested using MacOS Sierra, Version 10.12.6 on February 7, 2018. There is also a requirement for \(at least\) Xcode 7; we tested with Xcode 8.3.3._

If you face any complications, please refer to the [official instructions](http://www.openstm32.org/Installing%2BSystem%2BWorkbench%2Bfor%2BSTM32%2Bwith%2Binstaller) \(MacOS installation instructions are at the bottom\) and/or to the forums \(you need to be logged in to see the instructions\). Below we provide the instructions that worked for our system setup.

1\) From a terminal, navigate to the directory where the downloaded RUN and checksum files are located. Check the permissions with the following command:

```bash
$ ls -l
```

If you do not see an `x` in the permissions for the RUN file:

```bash
>> -rw-r--r--@ ... install_sw4stm32_macos_64bits-vX.X.run
```

You will have to give execution rights to the file as such:

```bash
$ chmod 755 install_sw4stm32_macos_64bits-vX.X.run
```

The `ls -l` command should then show something like:

```bash
>> -rwxr-xr-x@ ... install_sw4stm32_macos_64bits-vX.X.run
```

You can now run the installation file as so:

```bash
$ ./install_sw4stm32_macos_64bits-vX.X.run
```

The checksum file will be used to check the download integrity which may take some time. Eventually, a window pane similar to below should pop up.

![](../../.gitbook/assets/mac_install_1.png)

2\) You will have to accept two license agreements to proceed with the installation, after which you will be asked to specify the installation path \(see below\). If the path does not exist, you will be asked to create the directory.

![](../../.gitbook/assets/mac_install_4.png)

3\) Next, you can select which packs to install; leave as is. You will then be asked to confirm your installation path and packs to install. Pressing "Next" will start the installation \(see below\).

![](../../.gitbook/assets/mac_install_6-1-1.png)

![](../../.gitbook/assets/mac_install_7-1-1.png)

_Note: the instructions were tested using MacOS Mojave, Version 10.14 on October 1, 2019._

You may encounter the following dialog on macOS, please follow the instructions below if it is your case:

![](../../.gitbook/assets/screenshot-2019-09-25-at-17.06.48.png)

1\) Open your _System Preferences_ and navigate to _Security & Privacy:_

![](../../.gitbook/assets/mac_install_11.png)  
After setting the workspace, you should see a window pane similar to below.

3\) After letting MacOS open the install package, you should be able to pursue the normal installation.

You can now proceed to creating [your first project](../instructions.md)!

