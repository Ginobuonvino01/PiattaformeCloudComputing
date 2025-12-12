from openstack import connection


def connect(self):
    """Connessione a DevStack"""
    try:
        self.conn = connection.Connection(
            auth_url=self.auth_url,
            username=self.username,
            password=self.password,
            project_name=self.project_name,
            user_domain_name="default",
            project_domain_name="default",
            identity_api_version="3",
            region_name="RegionOne"
        )

        # Test con un'operazione semplice
        list(self.conn.compute.hypervisors())
        print(f"✅ Connesso a OpenStack DevStack: {self.auth_url}")
        return True
    except Exception as e:
        print(f"❌ Errore connessione OpenStack DevStack: {e}")
        print("   Controlla che DevStack sia avviato: cd ~/devstack && ./stack.sh")
        return False