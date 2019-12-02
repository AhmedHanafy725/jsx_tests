from jumpscale import j

iyo_name = self.random_string()
iyo = j.clients.itsyouonline.get(
    iyo_name, baseurl="https://itsyou.online/api", application_id=self.iyo_id, secret=self.iyo_secret
)
self.jwt = iyo.jwt_get(scope="user:memberof:threefold.sysadmin").jwt
self.ssh_key = self.load_ssh_key()
self.media = []
self.flist = ""
self.container_name = self.random_string()
self.node_ip = self.get_node()
self.client_name = self.random_string()
self.node = j.clients.zos.get(self.client_name, host=self.node_ip, password=self.jwt)
self.port = random.randint(2000, 3000)
self.ports = {self.port: 22}
self.container_id = self.node.client.container.create(
    name=self.vm_name,
    root_url=self.flist,
    port=self.ports,
    nics=[{"type": "default"}],
    config={"/root/.ssh/authorized_keys": self.ssh_key},
).get()
