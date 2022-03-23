import paramiko
import time
from termcolor import colored
from timeit import default_timer as timer

global password
username = "LDAP"
password = "PWD"


def VPRN_implement(device_ip):
    producttype =""
    host_ci =""

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    file = open("logs/"+"results.log", "a")

    try:
        remote_connection = ssh.connect(device_ip, port="22", username=username, password=password, timeout=10)
        remote_connection = ssh.invoke_shell()
        print (colored ("connected_ip_address_"+ device_ip,"blue"))

        ############################device_type_check##################################
        remote_connection.send("shoplay  current-configuration   | include  sysname"+"\n")
        time.sleep(1)
        output25 = remote_connection.recv(65535)
        result25 = output25.decode('ascii').strip("\n")
        output_list_ciname = result25.splitlines()

        for j in (output_list_ciname):
            if ("sysname" in j and "include" not in j):
                words = j.split()
                host_ci = words[1]
                print("host_cı="+host_ci)

        if ("nw_ra_m02f" in host_ci) or ("nw_ra_m02e" in host_ci) or ("nw_ra_m016" in host_ci) or ("nw_ra_a98c" in host_ci):
            producttype = "APE"

        elif ("nw_ts_a910"in host_ci):
            producttype = "ATN"

        print(producttype)

        ################################Template_Replace #######################################
        if producttype == "APE" :
            file2 = open("temps/"+'VPRN_temp_ape.txt', 'r')
            data1 = file2.read()

            newdata1 = data1.replace("ABCDE", device_ip)
            file2.close()
            file3 = open("temps/"+'VPRN_temp1_ape.txt', 'w')
            file3.write(newdata1)
            file3.close()
            time.sleep(3)

            f5 = open("temps/"+'VPRN_temp1_ape.txt', 'r')
            commands = f5.readlines()

        elif  producttype == "ATN" :

            file2 = open("temps/"+'VPRN_temp_atn.txt', 'r')
            data1 = file2.read()

            newdata1 = data1.replace("ABCDE", device_ip)
            file2.close()
            file3 = open("temps/"+'VPRN_temp1_atn.txt', 'w')
            file3.write(newdata1)
            file3.close()
            time.sleep(3)

            f5 = open("temps/"+'VPRN_temp1_atn.txt', 'r')
            commands = f5.readlines()

        elif producttype == "":
            f5 = open("temps/"+'no_command.txt', 'r')
            commands = f5.readlines()
            print("There is issue in Ne Type !!!")

        ################################Send Command  ######################################
        remote_connection.send("sys" + "\n")
        time.sleep(1)
        for command in commands:
            remote_connection.send(command+ " \n")
            time.sleep(1)
            output2 = remote_connection.recv(65535)
            result2 = output2.decode('ascii').strip("\n")
            file.write(result2)
            print(result2)

        remote_connection.send("return" + "\n")
        time.sleep(1)
        remote_connection.send("save " + " \n")
        time.sleep(1)
        remote_connection.send("y" + " \n")
        time.sleep(1)
        output3 = remote_connection.recv(65535)
        result3 = output3.decode('ascii').strip("\n")
        file.write(result3)
        print(result3)

        #####################################VPRN Route Control#############################

        ssh.close()


    except Exception as e:
        print(device_ip +"\n"+ "no connection_to_device " + str(e), end=" ")
        print("\n")
        print(colored("Ipmlementation Failed, for "+device_ip+" Control SSH parameters or Do ip Manually !!","red"))
        time.sleep(2)
        with open("unreachables.txt", "a") as f:
            f.write(device_ip + "\n")
        f.close()


def new_VPRN_default_route_check (device_ip):
    try:
        default_route = []
        VPRN_default_route = "NOK"

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        remote_connection = ssh.connect(device_ip, port="22", username=username, password=password, timeout=10)
        remote_connection = ssh.invoke_shell()
        print(colored("connected_ip_address_" + device_ip, "blue"))
        print(colored("New VPRN Default Route Check Started !!" + device_ip, "blue"))


        i=0
        while i < 4 :
            i=i+1
            remote_connection.send("sho ip rou vpn 2G3G-DATA-ACCESS | inc 10.186.176.8/29 \n") ## New VPRN will be here
            time.sleep(2)
            output = remote_connection.recv(65535)
            result = output.decode('ascii').strip("\n")
            output_list_fnk = result.splitlines()
            print(result)

            for line_fnk in output_list_fnk:
                if ("10.186.176.8/29" in line_fnk and "RD" in line_fnk) :
                    VPRN_default_route = "OK"
                    words = line_fnk.split()
                    default_route.append(words[0])
                    i=6
                    break
            print(colored(" Refresh started pls wait 5 seconds !!", "yellow"))
            time.sleep(4)

        ssh.close()
        return VPRN_default_route


    except Exception as e:
        print(device_ip + "no connection_to_device " + str(e), end=" ")
        time.sleep(2)


while True :
    user_input = str(input("\n\n2G3G_SAME_VPRN_IMPLEMENTATION_SCRIPT\n\n""type_1_for_2G3G_SAME_VPRN__Implementation\ntype_2_for_quit\n"))
    if user_input == "1":
        f1 = open('hostfile.txt', 'r')
        f2= open("implement_ok.txt",'a')
        f3 = open("implement_nok.txt", 'a')
        devices = f1.readlines()
        for device in devices:
            column = device.split()
            host = str(column[0])
            t1_start = timer()
            VPRN_implement(host)

            if new_VPRN_default_route_check(host) == "OK":
                f2.write(host+"\n")
                print(colored("VPRN Route Status is OK", "blue"))
            else :
                f3.write(host+"\n")
                print(colored("VPRN Route Status is NOK !!!", "red"))

            t1_stop = timer()
            print("Elapsed time during the whole program in seconds:",
                  int(t1_stop) - int(t1_start))
            time.sleep(2)
        f1.close()
        f2.close()
        f3.close()


    elif user_input == "2" :
        print ("Logout....")

        break



