Install avocado
===============

- Fedora
    1. > sudo curl https://repos-avocadoproject.rhcloud.com/static/avocado-fedora.repo -o /etc/yum.repos.d/avocado.repo
    2. > sudo dnf repolist avocado avocado-lts
    3. > sudo dnf install avocado
    
- Generic installation from a git repository
    1. > sudo yum install -y git gcc python-devel python-pip libvirt-devel libyaml-devel redhat-rpm-config xz-devel
    2. > git clone git://github.com/avocado-framework/avocado.git
    3. > cd avocado
    4. > sudo make requirements
    5. > sudo python setup.py install

Note that python and pip should point to the Python interpreter version 2.7.x. 
