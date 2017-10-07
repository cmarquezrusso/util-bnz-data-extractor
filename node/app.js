var express = require("express");
var app = express();
var elasticsearch = require("elasticsearch");

var client = new elasticsearch.Client({
	host: "elasticsearch:9200",
	log: "trace"
});

app.get("/transactions/:from/:size", function(req, res) {
	client
		.search({
			index: "bank",
			type: "transactions",
			body: {
				from: req.params.from,
				size: req.params.size,
				sort: [
					{
						timestamp: { order: "desc" }
					}
				],
				query: {
					match_all: {}
				}
			}
		})
		.then(
			function(resp) {
				var hits = resp.hits.hits;
				res.send(hits);
			},
			function(err) {
				console.trace(err.message);
				res.send(err.message);
			}
		);
});

app.get("/search/:query", function(req, res) {
	client
		.search({
			index: "bank",
			type: "transactions",
			body: {
				sort: [
					{
						timestamp: { order: "desc" }
					}
				],
				query: {
					match: {
						description: req.params.query
					}
				}
			}
		})
		.then(
			function(resp) {
				var hits = resp.hits.hits;
				res.send(hits);
			},
			function(err) {
				console.trace(err.message);
				res.send(err.message);
			}
		);
});

app.listen(3000, function() {
	console.log("Example app listening on port 3000!");
});
