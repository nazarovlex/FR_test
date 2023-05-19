db = db.getSiblingDB("web")
if (db.getUser("owner") === null) {
    db.createUser({
        user: "owner",
        pwd: "password",
        roles: [
            {
                role: "dbOwner",
                db: "web"
            },
        ]
    })
}
