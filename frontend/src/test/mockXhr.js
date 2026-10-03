/**
 * Reusable mock XMLHttpRequest implementation for Vitest unit tests
 */
export class MockXMLHttpRequest {
  constructor() {
    this.headers = {};
    this.upload = {
      onprogress: null,
    };
    this.onload = null;
    this.onerror = null;
    this.ontimeout = null;
    this.status = 200;
    this.statusText = 'OK';
    this.responseText = '';
    this.url = '';
    this.method = 'GET';
    this.sentData = null;
    this.aborted = false;

    // Track instance globally for test triggers
    MockXMLHttpRequest.lastInstance = this;
    MockXMLHttpRequest.instances.push(this);
  }

  open(method, url) {
    this.method = method;
    this.url = url;
  }

  setRequestHeader(key, value) {
    this.headers[key] = value;
  }

  send(data) {
    this.sentData = data;
    // Auto-respond if a mock responder is registered
    if (MockXMLHttpRequest.autoResponder) {
      setTimeout(() => {
        if (!this.aborted) {
          MockXMLHttpRequest.autoResponder(this);
        }
      }, 0);
    }
  }

  abort() {
    this.aborted = true;
  }

  // Test helper methods to trigger lifecycle events
  triggerProgress(loaded, total) {
    if (this.upload.onprogress) {
      this.upload.onprogress({
        lengthComputable: true,
        loaded,
        total,
      });
    }
  }

  triggerLoad(status, responseData) {
    this.status = status;
    this.responseText = typeof responseData === 'string' ? responseData : JSON.stringify(responseData);
    if (this.onload) {
      this.onload();
    }
  }

  triggerError() {
    if (this.onerror) {
      this.onerror();
    }
  }
}

MockXMLHttpRequest.instances = [];
MockXMLHttpRequest.lastInstance = null;
MockXMLHttpRequest.autoResponder = null;

MockXMLHttpRequest.reset = () => {
  MockXMLHttpRequest.instances = [];
  MockXMLHttpRequest.lastInstance = null;
  MockXMLHttpRequest.autoResponder = null;
};
