import { identity } from 'angular';
import { API, TOKENS } from './api-strings';
import { parseXML } from '../utils/parser';

/* global FormData */

export class ValidatorService {
  constructor($http) {
    'ngInject';

    this.http = $http;
  }

  postValidate(type, validation) {

    var type_arg = ""
    if(type == 'function'){
      type_arg = "function=true&"
    }
    if(type == 'service'){
      type_arg = "service=true&"
    }
    if(type == 'project'){
      type_arg = "project=true&"
    }
    var funcion = "function=true&";
    var sync = "sync=true&";
    var source = `source=${validation.source}&`;
    var path = `path=${validation.path}&`;
    var syntax = `syntax=${validation.syntax}&`;
    var integrity = `integrity=${validation.integrity}&`;
    var topology = `topology=${validation.topology}&`;
    var custom = `custom=${validation.custom}&`;
    var cfile = `cfile=${validation.cfile}&`;
    var dpath = `dpath=${validation.dpath}&`;
    var dext = `dext=yml`
    var endpoint = 'http://localhost:5001/api/v1/validations?'
    if(validation.workspace != ''){
      var workspace = `workspace=${validation.workspace}&`
      var request_url = endpoint.concat(type_arg,sync,source,path,syntax,integrity,topology,custom,cfile,dpath,workspace,dext);
    }
    else{
      var request_url = endpoint.concat(type_arg,sync,source,path,syntax,integrity,topology,custom,cfile,dpath,dext);
    }
    return this.http.post(request_url)
      .then(response => response.data);
  }

  getValidations(){
    var endpoint = 'http://localhost:5001/api/v1/validations';
    return this.http.get(endpoint).then(response => response.data);
  }

  getValidationById(id){
    var endpoint = 'http://localhost:5001/api/v1/validations/'.concat(id);
    return this.http.get(endpoint).then(response => response.data);
  }

  getReports() {
    return this.http.get(API.report.list)
      .then(response => response.data);
  }

  getReportResult(id) {
    var endpoint = 'http://localhost:5001/api/v1/validations/'.concat(id);
    return this.http.get(endpoint).then(response => response.data);
  }

  getReportTopology(id) {
    var endpoint = 'http://localhost:5001/api/v1/validations/'.concat(id, "/topology");

    var xmlDoc;
    return this.http.get(endpoint).then(response => {
        xmlDoc = new DOMParser().parseFromString(response.data, 'text/xml');
        return parseXML(xmlDoc);
      }).catch(err => {
      });
    }



  getReportFWGraphs(id) {
    // return this.http.get(API.report.single.fwgraph.replace(TOKENS.id, id))
    //   .then(response => response.data);
    var endpoint = 'http://localhost:5001/api/v1/validations/'.concat(id, "/fwgraph");
    return this.http.get(endpoint).then(response => response.data);
  }

  getResources() {
    return this.http.get(API.resources);
  }

  getWatches() {
    return this.http.get(API.watches);
  }
}

export default ValidatorService;
