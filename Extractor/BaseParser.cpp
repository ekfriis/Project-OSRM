/*
open source routing machine
Copyright (C) Dennis Luxen, others 2010

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU AFFERO General Public License as published by
the Free Software Foundation; either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
or see http://www.gnu.org/licenses/agpl.txt.
*/

#include "BaseParser.h"

BaseParser::BaseParser(ScriptingEnvironment& se) : use_route_relations(false) {
    ReadUseRouteRelationSetting(se.getLuaStateForThreadID(0));
}

void BaseParser::ReadUseRouteRelationSetting(lua_State* luaState) {
    if( 0 != luaL_dostring( luaState, "return use_route_relations\n") ) {
        ERR(lua_tostring( luaState,-1)<< " occured in scripting block");
    }
    if( lua_isboolean( luaState, -1) ) {
        use_route_relations = lua_toboolean(luaState, -1);
    }
    if( use_route_relations ) {
        INFO("Using route relations" );
    } else {
        INFO("Ignoring route relations" );
    }
}
