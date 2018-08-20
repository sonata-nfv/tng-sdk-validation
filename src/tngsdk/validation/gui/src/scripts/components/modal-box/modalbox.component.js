import template from './modalbox.html';

export const ModalBoxComponent = {

  template,
  bindings: {
    isHidden: '<',
    onClose: '&',
    onIdChange: '&',
  },
  controller: class ModalBoxComponent {

    constructor(ValidatorService, $scope) {
      'ngInject';

      this.validatorService = ValidatorService;
      this.scope = $scope;
      this.prevReports = [];
      this.validation = {
        path: '',
        source: '',
        integrity: false,
        topology: false,
        syntax: false,
        custom: false,
        cfile: '',
        file: null,
        dpath: '',
        workspace: '',
      };
      this.hasErrors = false;
      this.errorMessage = 'Errors in validation...';
      this.hasNoErrors = false;
      this.type = '';
      this.strings = {
        options: ['project', 'package', 'service', 'function'],
        sources: ['local', 'url', 'embedded'],
      };
      this.scope.files = [];
    }

    $onInit() {
      this.validation.source = this.strings.sources[0];
      this.type = this.strings.options[0];

      this.scope.$watchCollection('files', (value) => {
        //  this.enableButton = (value.length > 0);
        if (value && value.length > 0) {
          this.validation.file = value[0];
        }
      });
    }

    $onChanges(changesObj) {
      if (changesObj.isHidden !== undefined) {
        if (!changesObj.isHidden.currenValue) {
          this.openModal();
        }
      }
    }

    openModal() {
      this.listReports();
    }

    listReports() {
      this.prevReports.length = 0;
      this.validatorService.getValidations()
        .then((validations) => {
          Object.keys(validations).forEach((id) => {
            const repo = validations[id];
            this.prevReports.push({
              id,
              flags: ModalBoxComponent.translateFlags(repo),
              path: repo.path,
              type: repo.type,
              errors: repo.result.error_count,
            });
          });
        });
    }

    static translateFlags(repo) {
      const { topology, syntax, integrity, custom } = repo;

      return `${syntax ? 'S' : ''}${integrity ? 'I' : ''}${topology ? 'T' : ''}${custom ? 'C' : ''}`;
    }

    getTopology(id, path) {
      this.onIdChange({
        $event: { id, path },
      });

      this.closeModal();
    }

    validate(isValid) {
      this.hasErrors = false;
      this.hasNoErrors = false;
      if (isValid) {
        this.validatorService.postValidate(this.type, this.validation)
          .then((response) => {
            this.listReports();
            if(response.result.error_count != 0){
              this.hasErrors = true;
            }else{
              this.hasNoErrors = true;
            }
          })
      }


    }

    closeModal() {
      this.onClose();
    }
  },
};

export default ModalBoxComponent;
