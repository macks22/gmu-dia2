var Bookshelf = require('bookshelf');

Bookshelf.MySql = Bookshelf.initialize({
    client: 'mysql',
    connection: {
        host: 'dll.gmu.edu',
        user: dia2,
        password: N$f*dll!,
        database: nsf,
        charset: UTF8_GENERAL_CI,
    }
});

var Award = Bookshelf.Model.extend({

    tableName: 'award'

});

/*
create table award (
        awd_id INT(11) NOT NULL primary key,
        awd_title VARCHAR(250) NOT NULL DEFAULT '',
        awd_effective_date DATE DEFAULT NULL,
        awd_expiration_date DATE DEFAULT NULL, 
        awd_amount INT(11) NOT NULL DEFAULT 0,
        awd_instrument VARCHAR(30) NOT NULL DEFAULT '',
        awd_org_code INT(11) NOT NULL DEFAULT 0,
        awd_org_directorate VARCHAR(100) NOT NULL DEFAULT '',
        awd_org_division VARCHAR(100) NOT NULL DEFAULT '',
        awd_program_officer VARCHAR(150) NOT NULL DEFAULT '',
        awd_abstract VARCHAR(5000) NOT NULL DEFAULT '',
        awd_min_amd_date DATE DEFAULT NULL,
        awd_max_amd_date DATE DEFAULT NULL,
        awd_arra_amount int(11),
        awd_year INT(5)
        )
engine=InnoDB;
*/

var Investigator = Bookshelf.Model.extend({

    tableName: 'investigator'

});

/*
create table investigator (
        inv_id INT(11) NOT NULL auto_increment primary key,
        inv_first_name VARCHAR(20) NOT NULL DEFAULT '',
        inv_last_name VARCHAR(100) NOT NULL DEFAULT '',
        inv_email VARCHAR(200) NOT NULL DEFAULT '',
        inv_start_date DATE DEFAULT NULL, 
        inv_end_date DATE DEFAULT NULL, 
        inv_role VARCHAR(100) NOT NULL DEFAULT '',
        fk_awd_id INT(11) NOT NULL DEFAULT 0
        )
engine=InnoDB;
*/

var Institution = Bookshelf.Model.extend({

    tableName: 'institution'

});

/*
create table institution (
        inst_id INT(11) NOT NULL auto_increment primary key,
        inst_name VARCHAR(300) NOT NULL DEFAULT '',
        inst_city VARCHAR(200) NOT NULL DEFAULT '',
        inst_zip VARCHAR(10) NOT NULL DEFAULT '',
        inst_phone VARCHAR(20) NOT NULL DEFAULT '',
        inst_street VARCHAR(300) NOT NULL DEFAULT '',
        inst_state VARCHAR(30) NOT NULL DEFAULT '',
        inst_state_code VARCHAR(5) NOT NULL DEFAULT '',
        inst_country VARCHAR(200) NOT NULL DEFAULT '',
        fk_awd_id INT(11) NOT NULL DEFAULT 0
        )
engine=InnoDB;
*/

new Award({'awd_year': 1995})
    .fetch()
    .then(function (model) {
        console.log(model);
    });

