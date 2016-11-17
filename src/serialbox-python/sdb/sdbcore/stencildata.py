#!/usr/bin/python3
# -*- coding: utf-8 -*-
##===-----------------------------------------------------------------------------*- python -*-===##
##
##                                   s e r i a l b o x
##
## this file is distributed under terms of bsd license.
## see license.txt for more information.
##
##===------------------------------------------------------------------------------------------===##

from .logger import Logger


class StencilData(object):
    def __init__(self, serializer_data):

        # Data
        self.__serializer_data = serializer_data
        self.__serializer_data.register_as_listener(self.reset)

        self.__stencil_list_changed = False
        self.__stencil_list = []
        self.__stencil_idx_selected = -1

        self.__field_list_changed = False
        self.__field_list = []

        # Listeners
        self.__stencil_list_listener = []
        self.__field_list_listener = []

        self.reset()

    def reset(self):
        Logger.info("Updating StencilData of '%s'" % self.__serializer_data.name)

        # Possibly a new Serializer
        self.__stencil_list_changed = True

        # Get new list of stencils
        self.update_stencil_list()

        # Update the available list of fields
        if self.__stencil_list:
            self.set_selected_stencil(0)

    def update_stencil_list(self):
        """Update the avialable stencils.
        """
        if not self.__stencil_list_changed:
            return

        Logger.info("Updating list of stencils of StencilData '%s'" % self.__serializer_data.name)

        serializer = self.__serializer_data.serializer
        if serializer and serializer.global_metainfo.has_key("stencils"):
            stencil_list = serializer.global_metainfo["stencils"]

            if stencil_list != self.__stencil_list:
                # Inform listener that we removed all items
                for listener in self.__stencil_list_listener:
                    listener.remove_all_items()

                # Inform listener that we added new items
                self.__stencil_list = stencil_list
                for stencil in self.__stencil_list:
                    for listener in self.__stencil_list_listener:
                        listener.add_item(stencil)
            else:
                self.__stencil_list = stencil_list

            self.__stencil_list_changed = False

    def update_field_list(self):
        """Update field list according to the selected stencil
        """
        if not self.__field_list_changed:
            return

        Logger.info("Updating field list of StencilData '%s' to match stencil '%s'" % (
            self.__serializer_data.name, self.selected_stencil))

        serializer = self.__serializer_data.serializer

        # If stencil list is empty -> exit
        if not self.__stencil_list:
            return

        # Get list of fileds of the current stencil
        field_list = []
        for sp in serializer.savepoint_list():
            if sp.name.startswith(self.__stencil_list[self.__stencil_idx_selected]):
                for fields in serializer.fields_at_savepoint(sp):
                    field_list += [fields]

        # Remove duplicates
        field_list = list(set(field_list))

        if self.__field_list != field_list:
            # Inform listener that we removed all items
            for listener in self.__field_list_listener:
                listener.remove_all_items()

            # Inform listener that we added new items
            self.__field_list = field_list
            for field in self.__field_list:
                for listener in self.__field_list_listener:
                    listener.add_item(field)
        else:
            self.__field_list = field_list

        self.__field_list_changed = False

    def set_selected_stencil(self, idx):
        self.__stencil_idx_selected = 0 if idx < 0 else idx
        self.__field_list_changed = True
        self.update_field_list()

    @property
    def serializer(self):
        return self.__serializer_data.serializer

    @property
    def stencil_list(self):
        return self.__stencil_list

    @property
    def field_list(self):
        return self.__field_list

    @property
    def selected_stencil(self):
        return "<not-set>" if not self.__stencil_list else self.__stencil_list[
            self.__stencil_idx_selected]
    @property
    def name(self):
        return self.__serializer_data.name

    def register_as_stencil_list_listener(self, listener):
        self.__stencil_list_listener += [listener]

    def register_as_field_list_listener(self, listener):
        self.__field_list_listener += [listener]