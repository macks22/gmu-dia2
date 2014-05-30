var _ = require('lodash');
var Models = require('../db/models');

var validProperties = [
    'id',
    'title',
    'effective_date',
    'expiration_date',
    'amount',
    'instrument',
    'org_code',
    'org_directorate',
    'org_division',
    'program_officer',
    'abstract',
    'min_amd_date',
    'max_amd_date',
    'arra_amount',
    'year'
];

var exists = function (x) {
    return x != null;
}

var validProperty = function (property) {
    return _.indexOf(validProperties, property) !== -1;
}

var parseValidProperties = function (query) {
    var properties = {};

    _.forOwn(query, function (value, key) {
        if (validProperty(key)) {
            properties['awd_' + key] = value;
        }
    });

    return properties;
}

/*
 * GET a particular award.
 */
exports.findAward = function (req, res) {
    var json;
    var properties = parseValidProperties(req.query);

    console.info(properties);
    new Models.Award(properties)
        .fetch()
        .then(function (award) {
            if (exists(award)) {
                json = award.toJSON()
                console.log(json.awd_id)
                res.send(json);
            }
        });
};

exports.findAwards = function (req, res) {
    var json;
    var properties = parseValidProperties(req.query);

    console.info(properties);
    new Models.Awards(properties)
        .fetch()
        .then(function (awards) {
            if (exists(awards)) {
                json = awards.toJSON();
                res.send(json);
            }
        });
};

