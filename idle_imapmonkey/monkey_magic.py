import imaplib
from threading import Timer


#Exchange server I do testing on gives 5 IDLE updates for every event
#This is to make sure that all updates for an event are recieved.
TIMER_DELAY = 3

CRLF = imaplib.CRLF
imaplib.Commands.update({'DONE': ('IDLE',), 'IDLE': ('SELECTED',),})

__all__ = ["IMAP4", "IMAP4_stream", "Internaldate2tuple",
           "Int2AP", "ParseFlags", "Time2Internaldate"]

Internaldate2tuple = imaplib.Internaldate2tuple
Time2Internaldate = imaplib.Time2Internaldate
Int2AP = imaplib.Int2AP
ParseFlags = imaplib.ParseFlags
IMAP4_PORT = imaplib.IMAP4_PORT
IMAP4_SSL_PORT = imaplib.IMAP4_SSL_PORT
AllowedVersions = imaplib.AllowedVersions

def _get_Debug():
    return imaplib.Debug
def _set_Debug(val):
    imaplib.Debug = val
Debug = property(_get_Debug, _set_Debug)

class idle_mixin(object):
    
    def done(self):
        '''
        Use this method to tell the server to quit IDLE mode and resume normal operations.
        '''
        name = 'DONE'
        self.send('%s%s' % (name, CRLF))
        return

    def _bounce_idle(self):
        if self.state != 'IDLE':
            return
        self.done()
        self.idle()

    def idle(self, bounce_timer = (29 * 60) ):
        '''
        Use this method to initiate IDLE mode.

        bounce_timer: The IDLE spec suggests stopping and restarting IDLE
            every 29 minutes in order to avoid timing out. This is the default,
            and there should be no need to change it. If you find that your 
            connection is timing out anyway however change this value to something
            lower.

        Note that this method is blocking and should be run in a thread.
        '''
        name = 'IDLE'

        if name not in self.capabilities:
            raise self.Abort('Server does not support IDLE')
        tag = self._new_tag()
        data = '%s %s' % (tag, name)
        self.send('%s%s' % (data, CRLF))

        response = self._get_line()
        if 'accepted, awaiting DONE command' in response or 'idling' in response:
            self.state = name
            tmr = Timer(bounce_timer, self._bounce_idle)
            tmr.daemon = True
            tmr.start()
            final_response = self._coreader(tag)
            tmr.cancel()
            return final_response
        else:
            self.Abort('Failed to initiate IDLE! Got error %s' % response)

    def _coget_tagged_response(self, tag):
        while 1:
            result = self.tagged_commands[tag]
            if result is not None:
                del self.tagged_commands[tag]
                self.state = 'SELECTED'
                yield result
                return

            # Some have reported "unexpected response" exceptions.
            # Note that ignoring them here causes loops.
            # Instead, send me details of the unexpected response and
            # I'll update the code in `_get_response()'.

            try:
                yield self._get_response()
            except self.abort, val:
                if __debug__:
                    if self.debug >= 1:
                        self.print_log()
                raise

    def _coreader(self, tag):
        data_release = None
        resp_buffer = []

        coget = self._coget_tagged_response(tag)
        while 1:
            try:
                resp = coget.next()
            except StopIteration:
                return resp

            if self.state == 'IDLE':
                try: data_release.cancel()
                except AttributeError:
                    pass #quack!

            #TODO: cleanup resp data before dispatch
            resp_buffer.append(resp)

            if self.state == 'IDLE':
                data_release = Timer(TIMER_DELAY, self._idle_dispatch, (resp_buffer,))
                data_release.start()

    def _idle_dispatch(self, resp_buffer):
        '''
        This is required to clean out the response buffer so we don't process
        any messages more than once.
        '''
        try:
            return self.idle_dispatch(resp_buffer)
        finally:
            del resp_buffer[:]

    def idle_dispatch(self, resp_buffer):
        '''
        Reimplement this method in order to use the updates received from the IMAP server.
        
        Some ideas on what to do with the information received:
            -print notices to console
            -send the notices to inotify
            -send the notices to another IMAP connection in order to download the message
            -send the notices out over dbus.
        '''
        raise NotImplemented


class IMAP4(imaplib.IMAP4, idle_mixin):
    __doc__ = imaplib.IMAP4.__doc__

class IMAP4_SSL(imaplib.IMAP4_SSL, idle_mixin):
    __doc__ = imaplib.IMAP4_SSL.__doc__

class IMAP4_stream(imaplib.IMAP4_stream, idle_mixin):
    __doc__ = imaplib.IMAP4_stream.__doc__
