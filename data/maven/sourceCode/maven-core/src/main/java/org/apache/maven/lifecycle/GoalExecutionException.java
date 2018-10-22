package org.apache.maven.lifecycle;

/* ====================================================================
 *   Copyright 2001-2004 The Apache Software Foundation.
 *
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 * ====================================================================
 */

/**
 * @author <a href="mailto:jason@maven.org">Jason van Zyl </a>
 * @version $Id: GoalExecutionException.java,v 1.3 2004/12/25 16:26:24 jvanzyl
 *          Exp $
 */
public class GoalExecutionException
    extends Exception
{
    public GoalExecutionException( String message )
    {
        super( message );
    }

    public GoalExecutionException( Throwable cause )
    {
        super( cause );
    }

    public GoalExecutionException( String message, Throwable cause )
    {
        super( message, cause );
    }
}