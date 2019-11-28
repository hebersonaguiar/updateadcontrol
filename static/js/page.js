class TemplateSystem {

  constructor(name, template) {
    this.name = name;
    this.template = template;
    this._setUpTemplate();
  }

  _setUpTemplate() {
    this._cloneNavigation();
    this._setMenuBehavior();
    this._setDropdownBehavior();
    this._setSearchBehavior();
  }

  _cloneNavigation() {
    for (let navLogo of this.template.querySelectorAll('.page-wrapper .navigation .nav-logo')) {
      for (let logo of this.template.querySelectorAll('.header-bar .logo')) {
        let clonedLogo = logo.cloneNode(true);
        clonedLogo.classList.add('is-active');
        navLogo.appendChild(clonedLogo);
      }
      let backButton = window.document.createElement('button');
      backButton.setAttribute('data-level', 0);
      backButton.addEventListener('click', (event) => {
        this._onBackButtonClick(event);
      });
      navLogo.appendChild(backButton);
    }
    for (let navAvatar of this.template.querySelectorAll('.page-wrapper .navigation .nav-avatar')) {
      for (let avatar of this.template.querySelectorAll('.configs')) {
        navAvatar.appendChild(avatar.cloneNode(true));
      }
    }
    for (let navContrast of this.template.querySelectorAll('.page-wrapper .navigation .nav-contrast')) {
      for (let contrast of this.template.querySelectorAll('.contrast')) {
        navContrast.appendChild(contrast.cloneNode(true));
      }
    }
    for (let navBookmarks of this.template.querySelectorAll('.page-wrapper .navigation .nav-bookmarks')) {
      for (let bookmarks of this.template.querySelectorAll('.bookmarks')) {
        navBookmarks.appendChild(bookmarks.cloneNode(true));
      }
    }
    for (let navButtonTimeout of this.template.querySelectorAll('.page-wrapper .navigation .nav-buttontimeout')) {
      for (let logout of this.template.querySelectorAll('.logout')) {
        navButtonTimeout.appendChild(logout.cloneNode(true));
      }
    }
    for (let navTimeout of this.template.querySelectorAll('.page-wrapper .navigation .nav-logout .nav-timeout')) {
      for (let timeout of this.template.querySelectorAll('.timeout')) {
        navTimeout.appendChild(timeout.cloneNode(true));
      }
    }
  }

  _setMenuBehavior() {
    for (let menuHamburger of this.template.querySelectorAll('.menu-hamburger')) {
      menuHamburger.addEventListener('click', () => {
        for (let navigation of this.template.querySelectorAll('.navigation')) {
          navigation.classList.toggle('is-active');
          navigation.setAttribute('data-level', '0');
        }
      });      
    }
    for (let button of this.template.querySelectorAll('.page-wrapper .navigation .item button')) {
      let arrowIcon = document.createElement('i');
      arrowIcon.setAttribute('class', 'fas fa-chevron-right');
      button.appendChild(arrowIcon);
      if (window.screen.width < 1024) {
        button.addEventListener('click', (event) => {
          this._setMenuMobileBehavior(event);
        });
      } else {
        for (let navigation of this.template.querySelectorAll('.page-wrapper .navigation')) {
          if (!navigation.hasAttribute('data-children')) {
            if (button.parentNode.parentNode.getAttribute('data-level') == 0) {
              button.parentNode.classList.add('is-active');
            }
            button.addEventListener('click', () => {
              button.parentNode.classList.toggle('is-active');
            });
          }
        }
      }
    }
  }

  _setMenuMobileBehavior(event) {
    this.ongoingMenu = event.currentTarget;
    let currentMenuLevel = Number(this.ongoingMenu.nextElementSibling.getAttribute('data-level'));
    for (let button of this.template.querySelectorAll('.page-wrapper .navigation .item button')) {
      if (button === this.ongoingMenu) {
        button.parentNode.classList.add('is-active');
        for (let navigation of this.template.querySelectorAll('.page-wrapper .navigation')) {
          navigation.setAttribute('data-level', button.nextElementSibling.getAttribute('data-level'));
        }
      }
    }
    for (let backButton of this.template.querySelectorAll('.page-wrapper .navigation .nav-logo button')) {
      backButton.innerHTML = this.ongoingMenu.innerHTML;
      for (let icon of backButton.querySelectorAll('svg')) {
        icon.classList.remove('fa-chevron-right');
        icon.classList.add('fa-chevron-left');
      }
      backButton.classList.add('is-active');
      backButton.previousElementSibling.classList.remove('is-active');
      backButton.setAttribute('data-level', currentMenuLevel);
    }
  }

  _onBackButtonClick(event) {
    for (let button of this.template.querySelectorAll('.page-wrapper .navigation .item button')) {
      if (button === this.ongoingMenu) {
        button.parentNode.classList.remove('is-active');
        for (let navigation of this.template.querySelectorAll('.page-wrapper .navigation')) {
          navigation.setAttribute('data-level', button.parentNode.parentNode.getAttribute('data-level'));
        }
        event.currentTarget.setAttribute('data-level', button.parentNode.parentNode.getAttribute('data-level'));
        if (button.parentNode.parentNode.getAttribute('data-level') == 0) {
          event.currentTarget.childNodes[0].nodeValue = '';
          event.currentTarget.classList.remove('is-active');
          event.currentTarget.previousElementSibling.classList.add('is-active');
          this.ongoingMenu = undefined;
        } else {
          this.ongoingMenu = button.parentNode.parentNode.previousElementSibling;
          event.currentTarget.childNodes[0].nodeValue = this.ongoingMenu.innerText;
        }
        break;
      }
    }
  }

  _setDropdownBehavior() {
    for (let dropdown of this.template.querySelectorAll('.dropdown')) {
      for (let trigger of dropdown.querySelectorAll('.trigger')) {
        trigger.addEventListener('click', () => {
          for (let menu of dropdown.querySelectorAll('.menu')) {
            menu.classList.toggle('is-active');
          }
        });
      }
    }
  }

  _setSearchBehavior() {
    for (let search of this.template.querySelectorAll('.search')) {
      if (window.screen.width >= 1024) {
        for (let input of search.querySelectorAll('input#search')) {
          input.addEventListener('focus', () => {
            search.classList.add('is-active')
          });
        }
      } else {
        for (let buttonSearch of search.querySelectorAll('.field button')) {
          buttonSearch.addEventListener('click', () => {
            search.classList.add('is-active');
          });
        }
      }
      for (let buttonClose of search.querySelectorAll('button.close')) {
        buttonClose.addEventListener('click', () => {
          search.classList.remove('is-active');
        });
      }
    }
  }
}

let systemList = [];

window.onload = (function() {
  for (let templateSystem of window.document.querySelectorAll('.template-system')) {
    systemList.push(new TemplateSystem('template-system', templateSystem));
  }
})();