# Installed_CDP (on ec2)

## 1. Instance Config

| **유 형**   | **상세 내역**                   |
| ----------- | ------------------------------- |
| OS          | `RHEL-7.9_HVM`                  |
| CDP_VERSION | `7.1.4`                         |
| INSTANCE    | `t2.xlarge` 이상 권고 드립니다. |
| STORAGE     | 100 GB                          |

 

![os](images\os.png)

 ![storage](images\storage.png)

 

## 2. Package install

1. yum install

   ![yum_install](images\yum_install.png)

   ```sh
   sudo yum update -y
   sudo yum install wget ntp iptables-services vim -y
   ```

   

2. ntpd 활성화

   ![activate_ntpd](images\activate_ntpd.png)

   ```sh
   # ntpd 활성화 
   sudo systemctl start ntpd
   sudo systemctl enable ntpd
   
   # ntpd 상시 활성화 
   sudo chkconfig ntpd on
   
   # ntpd 활성화 내역 확인 
   sudo chkconfig ntpd
   ```

   

3. ntpd를 활용한 rpm download & install

   ![download_rpm](images\download_rpm.png)

   ```sh
   wget https://rpmfind.net/linux/centos/7.9.2009/os/x86_64/Packages/libtirpc-devel-0.2.4-0.16.el7.x86_64.rpm
   sudo yum install libtirpc-devel-0.2.4-0.16.el7.x86_64.rpm -y
   ```

   

4. selinux disable

   ![set_selinux](images\set_selinux.png)

   ```sh
   # vi 수정을 통한 설정 변경  
   sudo vi /etc/selinux/config
   
   SELINUX=disabled 
   
   # linux 명령어 수행을 통한 값 변경
   sed -i 's/SELINUX= enforcing/SELINUX=disabled/' /etc/selinux/config
   
   ```

    

 

5. key-gen

   ![ssh-keygen](images\ssh-keygen.png)

   ```sh
   # 공개 키 생성
   ssh-keygen -t dsa -P '' -f ~/.ssh/id_dsa
   # 공개 키 내용 변경
   cat ~/.ssh/id_dsa.pub >> ~/.ssh/authorized_keys
   # 권한 변경
   chmod 0600 ~/.ssh/authorized_keys
   # test
   ssh localhost
   
   ```

   

### (Option) [Optimize performance]

(6) ~ (8) 항목은 option 사항이므로 미 수행 하여도 설치에 문제없습니다.
**[linux] vm.swappiness 설정**

> 1. 개요
>
>    - swappiness
>    - vm.swappiness
>
>    스왑 활용도, 스와핑 활용도, 스와피니스
>    리눅스 커널 속성 중 하나
>    스왑메모리 활용 수준 조절
>    스왑 사용의 적극성 수준
>
>     
>
> 2. 값 설명
>
>    값의 범위: 0 ~ 100 (기본값: 60)
>
>    | 값                  | 설명                 |
>    | ------------------- | -------------------- |
>    | vm.swappiness = 0   | 스왑 사용안함[1]     |
>    | vm.swappiness = 1   | 스왑 사용 최소화     |
>    | vm.swappiness = 60  | 기본값               |
>    | vm.swappiness = 100 | 적극적으로 스왑 사용 |

6. vm.swappiness option  

   ![swappiness1](images\swappiness1.png)

   ```sh
   sysctl vm.swappiness
   sudo sysctl vm.swappiness=1
   
   ```


   ![swappiness2](images\swappiness2.png)


   ```sh
   sudo su
   echo "vm.swappiness=1" >> /etc/sysctl.conf
   cat /etc/sysctl.conf
   
   ```

7. /etc/rc.d/rc.local 수정

   > **rc.local** 
   >
   > 부팅시 자동 실행 명령어 스크립트 수행 
   >
   > 일반적으로 서버 부팅시마다 매번 자동 실행되길 원하는 명령어는 /etc/rc.d/rc.local에 넣어주시면됩니다.
   >
   > **[THP(Transparent Huge Pages)](https://allthatlinux.com/dokuwiki/doku.php?id=thp_transparent_huge_pages_%EA%B8%B0%EB%8A%A5%EA%B3%BC_%EC%84%A4%EC%A0%95_%EB%B0%A9%EB%B2%95)**

   ![rc_local](images\rc_local.png)

   ```sh
   chmod +x /etc/rc.d/rc.local
   vi /etc/rc.d/rc.local
   
   # 하단의 내용 추가
   echo never > /sys/kernel/mm/transparent_hugepage/enabled
   echo never > /sys/kernel/mm/transparent_hugepage/defrag
    
   
   ```

   **THP 옵션이 활성화 확인 방법**

   ```sh
   cat /sys/kernel/mm/transparent_hugepage/enabled
   
   # [always] madvise never  -> 출력된 결과에 [always] 에 대괄호가 되어있으면 THP가 활성화 된 상태입니다.
   # always madvise [never]  -> 출력된 결과에 [never] 에 대괄호가 되어있으면 THP가 비활성화 된 상태입니다. 
   ```

   

8. /etc/default/grub 수정

   ![grub](images\grub.png)

   ```sh
   cat /etc/default/grub
   echo "transparent_hugepage=never" >> /etc/default/grub
   grub2-mkconfig -o /boot/grub2/grub.cfg
   
   systemctl start tuned
   tuned-adm off
   tuned-adm list
   systemctl stop tuned
   systemctl disable tuned
   
   ```

   
   

9. cloudera-manager-install

   1. installer download

      ```sh
      wget https://archive.cloudera.com/cm7/7.1.4/cloudera-manager-installer.bin
      sudo chmod u+x cloudera-manager-installer.bin
      sudo ./cloudera-manager-installer.bin
      ```

   2. install

      > next next next yes
      >
      > 명령어 입력없이 화면에서 엔터만 반복적으로 입력시 자동으로 설치 진행 
      >
      >  
      >
      > 설치 완료 후 아래의 링크로 접속 
      >
      > https://publicdns:7180

      | 설치 이미지                             |                                         |
      | --------------------------------------- | --------------------------------------- |
      | 1![installer_1](images\installer_1.png) | 2![installer_2](images\installer_2.png) |
      | 3![installer_3](images\installer_3.png) | 4![installer_4](images\installer_4.png) |

      ```sh
      # 서버 부팅 시 자동실행 설정
      sudo systemctl enable cloudera-scm-server.service
      ```

## 3. Multi node 설정

1. AMI 등록

   - Name : `cdp_ami`

   - Description : `Image for cdp cluster`

   - Storage : `100`

   - ![ami_register](images\ami_register.png)

     

2. Data node 생성
   등록된 AMI로 3개의 Instance 생성
   ![Data_nodes](images\Data_nodes.png)

3. Cluster Network 설정

   - 모든 node 설정

     ```sh
     sudo vi /etc/hosts
     
     
     # ==========================================================
     127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
     ::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
     
     
     10.0.1.235   cdp-manager
     10.0.1.22   cdp-node1
     10.0.1.228   cdp-node2
     10.0.1.112   cdp-node3
     
     ```


     Cloudera 재시작

     ```sh
     sudo service cloudera-scm-server restart
     ```

     

## 4. cloudera.manger 설정

1. cloudera.manger web install

   > 설치 완료 후 아래의 링크로 접속 
   >
   > http://{manager_server_publicdns}:7180
   >
   > ID : admin 
   >
   > PW : admin 

   ![cloudera_login](images\cloudera_login.png)

   > 무료 라이센스 사용 60일

   ![free_license](images\free_license.png)

   7-8 번 설치는 Issue가 있을 경우 1개 node 씩 수행

   | 설치 이미지                                           |                                                       |
   | ----------------------------------------------------- | ----------------------------------------------------- |
   | 1![cloudera_install_1](images\cloudera_install_1.png) | 2![cloudera_install_2](images\cloudera_install_2.png) |
   | 3![cloudera_install_3](images\cloudera_install_3.png) | 4![cloudera_install_4](images\cloudera_install_4.png) |
   | 5![cloudera_install_5](images\cloudera_install_5.png) | 6![cloudera_install_6](images\cloudera_install_6.png) |
   | 7![cloudera_install_7](images\cloudera_install_7.png) | 8![cloudera_install_8](images\cloudera_install_8.png) |
   | 9![cloudera_install_9](images\cloudera_install_9.png) |                                                       |

2. cloudera.manger web config
   6-7 번 설치는 Issue가 있을 경우 재수행

   | 설치 이미지                                                  |                                                     |
   | ------------------------------------------------------------ | --------------------------------------------------- |
   | 1![cloudera_config_1](images\cloudera_config_1.png)          | 2![cloudera_config_2](images\cloudera_config_2.png) |
   | 3![cloudera_config_3](images\cloudera_config_3.png)          | 4![cloudera_config_4](images\cloudera_config_4.png) |
   | 5![cloudera_config_5](images\cloudera_config_5.png)          | 6![cloudera_config_6](images\cloudera_config_6.png) |
   | 7![cloudera_config_6_success](images\cloudera_config_6_success.png) |                                                     |

3. cloudera.manger web 설치 완료 

   - 상태 체크 불량 시 해결 방법
     해당 node들은 정식 DNS가 제공된 상태가 아니기 때문에 상태 검사 시 오류가 발생
     DNS 상태 검사를 해제하면 해당 issue resolve 가능

     1. 상태 불량 host 접근
        ![health_check_resolve_1](images\health_check_resolve_1.png)

        ![health_check_resolve_2](images\health_check_resolve_2.png)

     2. DNS 상태 검사 해제

        ![health_check_resolve_3](images\health_check_resolve_3.png)

        ![health_check_resolve_4](images\health_check_resolve_4.png)

        ![health_check_resolve_5](images\health_check_resolve_5.png)

     

   - CDP-Cluster
     ![cloudera_cdp_cluster](images\cloudera_cdp_cluster.png)

